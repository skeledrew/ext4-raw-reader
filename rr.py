#! /bin/python

#  EXT4 Raw Reader: Read the raw contents of EXT4 partitions or their images for recovery, etc.
#  Copyright (C) 2015 Andrew Phillips <skeledrew@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Docstring template.
  
  Created:
   15-05-23
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   n/a
  History:
   n/a
  """
  
# Imports
import subprocess
import string
import time

"""Raw Reader.
  
  Created:
   14-07-??
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   TODO
    - superblock searcher
    - value mapper
    - flags mapper.
    - read extent tree
    - change to OOP
  History:
   n/a
"""

### Constants:
DEBUG = True
DD_BS = 512  # Bytes read & written by dd
S_STATE_FLAGS = [["1","Cleanly unmounted"],["2","Errors detected"],["4","Orphans being recovered"]]


### Functions:

# ok
def sys_call(cmd_line="ls -l", std_in=None):
  """Run and return the result of a shell command.
  
  Created:
   14-07-??
  Last Modified:
   14-07-??
   
  Params:
   cmd_line - Command line.
   std_in - ???
  Return:
   Stdout result.
  
  Notes:
   N/A
  History:
   14-07-??
    initial function.
   15-05-23
    added docstring.
  """
  
  if std_in != None:
    f = open("rr.tmp", "w")
    #print std_in
    f.write(std_in)
    f.close()
    std_in = f, f = std_in
  task = subprocess.Popen(cmd_line, shell=True, stdin=std_in, stdout=subprocess.PIPE)
  return task.stdout.read()

# ok
def dd_read(in_file, count=1, skip=0, in_flag="skip_bytes,count_bytes"):
  """Use dd command to raw read a file/device, return data read.
  
  Created:
   14-07-??
  Last Modified:
   14-07-??
   
  Params:
   in_file - Input file/device.
   count - Number of sectors (512B) to process.
   skip - Number of sectors to skip
   in_flags - see 'man dd'
  Return:
   Data as hex dump.
  
  Notes:
   N/A
  History:
   14-07-??
    initial function.
   15-05-23
    added docstring.
  """
  
  count = str(count)
  skip = str(skip)
  return sys_call("sudo dd if=" + in_file + " status=none skip=" + skip + " count=" + count + " | hexdump -Cv")

# ok
def grep_srch(std_in, pattern):
  """Basic search with grep.
  
  Created:
   14-07-??
  Last Modified:
   14-07-??
   
  Params:
   std_in - Data to search.
   pattern - Search pattern.
  Return:
   Stdout result.
  
  Notes:
   N/A
  History:
   14-07-??
    initial function.
   15-05-23
    added docstring.
  """
  with open("rr.tmp", "w") as f:
    f.write(std_in)
  return sys_call("sudo dd status=none if=rr.tmp | grep \"" + pattern + "\"")

# ok
def base_conv(value, src_base="16", dst_base="A"):
  """Base conversion.
  
  Created:
   14-07-??
  Last Modified:
   15-05-30
   
  Params:
   value - Value to be converted.
   src_base - Base of value.
   dst_base - Base to convert to.
  Return:
   Converted value.
  
  Notes:
   n/a
  History:
   15-05-30
    remove newline from return value (might have to recheck other functions that use it)
    added docstring
  """
  res = sys_call("echo 'ibase=" + src_base + ";obase=" + dst_base + ";" + value.upper() + "' | bc")
  if DEBUG and res == "":
    print "base_conv:", value
  return res.strip("\n")

# converts hex data to its actual value. test
def hex_conv(hex_data, size=[4,1,"le32"]):
  """Docstring template.
  
  Created:
   14-07-??
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   n/a
  History:
   n/a
  """
  value = []
  
  if size[0] > 1 and size[2][0:2] == "le":
    for inc in range(size[1]):
      unit = hex_data[inc * size[0] : inc * size[0] + size[0]]
      unit.reverse()
      value += unit
  
  elif size[2][0:1] == "u":
    value = hex_data
  value = "".join(value)
  if DEBUG and value == "":
    print "Error! hex_conv:", size, hex_data
    return "hex_conv error!"
  return base_conv(value)

  if d_type == "le32":
    # split into groups of 4, reverse and convert
    value = string.split(hex_data, " ")
    value.reverse()
    value = "".join(value)
    return base_conv(value)
  
  if d_type == "le16":
    # split into groups of 2
    value.reverse()
    value = "".join(value)
    return base_conv(value)
  
  if d_type == "u8":
    # check proper handling of array
    return base_conv(value)
  
  if d_type == "char":
    # convert to ASCII
    pass
  
  if d_type == "le64":
    # split into groups of 8, reverse and convert
    value = string.split(hex_data, " ")
    value.reverse()
    value = "".join(value)
    return base_conv(value)
  
# ok
def type_to_size(d_type):
  """Find and format the data size.
  
  Created:
   14-07-??
  Last Modified:
   15-05-26
   
  Params:
   d_type - Data type.
  Return:
   Array with type size and amount, and original data type.
    
  
  Notes:
   15-05-26
    new types should probably be added in hex_conv too...
  History:
   15-05-26
    added 'byte' data type
  """
  if d_type[-1] != "]":
    # add array indicator if there isn't any (simplifies things}
    d_type += "[1]"
  size = string.split(d_type, "[")
  size.append(size[0])
  size[1] = int(size[1][0:-1])  # all but last ']'
    
  if size[0] == "u8":
    size[0] = 1
    
  elif size[0] == "u32":
    size[0] = 4
  
  elif size[0] == "le16":
    size[0] = 2
    
  elif size[0] == "le32":
    size[0] = 4
    
  elif size[0] == "le64":
    size[0] = 8

  elif size[0] == "char":
    size[0] = 1
    
  elif size[0] == "byte":
    size[0] = 1
    
  else:
    print "\n", "Error: unimplemented data type: " + size[0] + " in type_to_size", "\n"
  return size

# ok
def hex_dump(hex_data):
  """Split and concatenate data forms.
  
  Created:
   15-05-30
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   n/a
  History:
   n/a
  """
  hex_data = string.split(hex_data, "\n")
  data = ""
  a_data = ""
  
  for line in hex_data:
    # concat lines of data (hex and ascii)
    if line[0] == "#":  # Ignore lines starting with '#'
      continue
    line = string.split(line, "  ")
    if len(line) == 1:
      break
    data += line[1] + " " + line[2] + " "
    a_data += line[3].strip("|")
  data = string.split(data.strip(' '), " ")
  return [data, a_data]

# ok
def data_parse(data, params="00 char[8] unknown", struct_size=1024, struct_rpt=1):
  """Create struct array of data.
  
  Created:
   15-05-30
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   n/a
  History:
   n/a
  """
  params = string.split(params, "\n")	
  hex_parse = []
  
  for rpt in range(struct_rpt):
    for line in params:
      if len(line) > 1 and line[0] == "#":  # Ignore lines starting with '#'
	continue
      line = string.split(line, " ")
      start = int(base_conv(line[0])) + rpt * struct_size
      size = type_to_size(line[1])
      stop = start + (size[0] * size[1])
      
      if size[2] == "char":
	element = data[1][start:stop]
      
      elif size[2] == "byte":
	element = ""
	for d in data[0][start:stop]:
	  element += d + " "
	element.strip(' ')
	  
      else:
	element = hex_conv(data[0][start:stop], size)
      
      if DEBUG and element == "":
	line.append("dump_parse error!")
	print "dump_parse:", data[start:stop]
      line.append(element)
      hex_parse.append(line)
  return hex_parse

# ok
def dump_parse(hex_data, params, struct_size=1024, struct_rpt=1):
  """Breaks apart 'hexdump -C' output using a struct.
  
  Created:
   14-07-??
  Last Modified:
   15-05-25
   
  Params:
   hex_data - Data to be formatted, from dd_read.
   params - Struct to format with.
    -> offset size label
   struct_size - Size of the struct
   struct_rpt - # times to process the struct
  Return:
   Array of data.
    [offset, label, value]
  
  Notes:
   15-05-26
    throws an error when there's an empty line in the struct file
     currently avoid by removing extra newlines
    need to find the proper way to handle 'byte'
  History:
   14-07-??
    initial function.
   15-05-23
    mod to allow .py comment lines in struct file
    added docstring.
   15-05-24
    mod to allow .py comment lines in hex dump
   15-05-25
    mod to process array of a struct
   15-05-26
    manage 'byte' type
  """
  return data_parse(hex_dump(hex_data), params, struct_size, struct_rpt)
    
# reads partition table on device
def part_read(src):
  pass

# ok
def file_read(n):
  with open(n,"r") as f:
    return f.read()

# test
def file_write(n, d):
  with open(n, "w") as f:
    f.write(d)
    
# print a struct that looks like possible GDTs
def unknown_struct1_print(src, skip, count, struct):
  data = string.split(dd_read(src, count, skip), "\n")
  
  for inc in range(len(data)/2):
    extract = data[inc*2] + "\n" + data[inc*2+1]
    
    res_struct = dump_parse(extract, struct)
    
    for res in res_struct:
      print res[0] +": " + res[2] + " = " + res[3].strip('\n')
    print "\n"
    
# read a struct array
def table_read(data, struct, struct_size):
  pass

# ok
def offset_to_block(offset, fix=0, size=DD_BS):
  """Convert hex offset to lba?
  
  Created:
   14-07-??
  Last Modified:
   15-06-01
   
  Params:
   offset - Hex offset value as string.
   fix - Number to add to converted value.
   size - Block size.
  Return:
   Array containing division and remainder?
  
  Notes:
   n/a
  History:
   15-05-24
    added 'fix' param to quickly modify value to a block boundary, etc
     (eg. use -56 to get superblock start)
    fixed type conversion.
   15-06-01
    param now used constant instead of literal.
  """
  block = []
  offset = int(base_conv(offset)) + fix
  block.append(offset / size)
  block.append(offset % size)
  return block

def find_sbs(source, start=0, count=2, dest=""):
  """Search a source for superblocks, return list of blocks.
  
  Created:
   15-05-24
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   n/a
  History:
   n/a
  """
  pass
  #dd if=15-04-06.img |hexdump -Cv |grep "53 ef" >sb-magic.txt

# ok
def pretty_parse(src, struct, out_file="", start=2, count=2):
  """Prettify parsed data with struct.
  
  Created:
   15-05-24
  Last Modified:
   n/a
   
  Params:
   src - File/device to read.
   start - # blocks to skip.
   count - # blocks to return.
   struct - Data struct to use.
  Return:
   Structured information.
  
  Notes:
   15-05-24
    use to extract and make data structures more human-readable
  History:
   15-05-25
    struct now an array taking name, size and repeats of a struct
     don't ask me why I did that...
  """
  res_struct = dump_parse(dd_read(src, count, start), file_read(struct[0]), struct[1], struct[2])
  info = ""
  
  for res in res_struct:
    info += res[0] +": " + res[2] + " = " + res[3].strip('\n') + '\n'
  
  if out_file != "":
    file_write(out_file, info)
  return info

def hex_to_bit(data):
  pass

def count_bits(data, bit):
  pass

# ok
def get_struct_value(struct, label):
  """Find a field value in a parsed data structure.
  
  Created:
   15-05-30
  Last Modified:
   n/a
   
  Params:
   struct - Structured data as returned by data_parse.
   label - Field from a struct file.
  Return:
   Data indexed by the field label.
  
  Notes:
   15-05-30
    convert any returned number to prevent bug; possible extra spaces returned in string
  History:
   n/a
  """
  for data in struct:
    if data[2] == label:
      return data[3]
  return "Error: Label " + label + " not found!"

# ok
def get_superblock(device, skip):
  """Returns a parsed superblock.
  
  Created:
   15-05-30
  Last Modified:
   15-05-31
   
  Params:
   device - Device/image to read.
   offset - Offset to superblock.
  Return:
   Parsed superblock.
  
  Notes:
   n/a
  History:
   15-05-31
    convert int strings to ints
     array has indexes that should be skipped
  """
  sb = dump_parse(dd_read(device, 2, skip), file_read("ext4_super_block.struct"))
  magic = int(get_struct_value(sb, "s_magic"))
  
  if magic != 61267:
    # magic check
    return ["Error: Invalid superblock!"]
  non_ints = [16, 23, 24, 28, 29, 30, 31, 32, 33, 34, 38, 42, 46, 49, 55, 61, 62, 72, 78, 79, 83, 84]
  
  for num in range(85):
    # convert strings to ints
    if non_ints.count(num) != 0:
      # skip non-ints
      continue
    #print num, sb[num][2], sb[num][3]
    sb[num][3] = int(sb[num][3])
  sb[6][3] = 2 ** (10 + sb[6][3])
  sb[7][3] = 2 ** sb[7][3]
  sb[11][3] = secs_to_dtime(sb[11][3])
  sb[12][3] = secs_to_dtime(sb[12][3])
  sb[16][3] = read_flags(sb[16][3], read_struct("s_state.flags"))
  sb[17][3] = read_opt(sb[17][3], read_struct("s_errors.opts"))
  sb[19][3] = secs_to_dtime(sb[19][3])
  #sb[20][3] = secs_to_dtime(sb[20][3])
  sb[21][3] = read_opt(sb[21][3], read_struct("s_creator_os.opts"))
  sb[22][3] = read_opt(sb[22][3], read_struct("s_rev_level.opts"))
  sb[28][3] = read_flags(sb[28][3], read_struct("s_feature_compat.flags"))
  sb[29][3] = read_flags(sb[29][3], read_struct("s_feature_incompat.flags"))
  sb[30][3] = read_flags(sb[30][3], read_struct("s_feature_ro_compat.flags"))
  sb[43][3] = read_opt(sb[43][3], read_struct("s_def_hash_version.opts"))
  sb[46][3] = read_flags(sb[46][3], read_struct("s_default_mount_opts.flags"))
  sb[48][3] = secs_to_dtime(sb[48][3])
  sb[55][3] = read_flags(sb[55][3], read_struct("s_flags.flags"))
  sb[60][3] = 2 ** sb[60][3]
  sb[69][3] = secs_to_dtime(sb[69][3])
  sb[74][3] = secs_to_dtime(sb[74][3])
  return sb

# ok
def secs_to_dtime(seconds):
  """Converts seconds since epoch to formatted date/time.
  
  Created:
   15-05-30
  Last Modified:
   15-06-03
   
  Params:
   seconds - Seconds since epoch time.
  Return:
   Formatted time.
  
  Notes:
   n/a
  History:
   15-06-03
    Added ternary operator to check for empty date.
  """
  return 0 if seconds == 0 else time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(seconds)))  # ternary op

# test
def read_flags(flags, values):
  """Read a set of flags.
  
  Created:
   15-05-30
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   15-05-31
    BUG: need to search the values instead of assume all bits are represented...
  History:
   n/a
  """
  set_flags = "|"
  flags = base_conv(flags, "16", "2")
  flags = flags[::-1]  # reverse string
  #print flags, len(flags), values
  
  for inc in range(len(flags)):
    if flags[inc] == "1":
      set_flags += values[inc][1] + "|"
  return set_flags

# ok
def read_struct(struct_file):
  """Load a struct from a file.
  
  Created:
   15-05-30
  Last Modified:
   n/a
   
  Params:
   struct_file - Name of file with the struct.
  Return:
   Struct as an array.
  
  Notes:
   15-05-30
    first line has the delimiter character
  History:
   n/a
  """
  struct = file_read(struct_file).split("\n")
  sep = struct[0]
  struct.remove(sep)
  new_struct = []
  
  for line in struct:
    if line[0] == "#":
      # skip comment line
      continue
    new_struct.append(line.split(sep))
  return new_struct

# ok
def read_opt(opt, opts):
  """Read an option.
  
  Created:
   15-05-30
  Last Modified:
   n/a
   
  Params:
   n/a
  Return:
   n/a
  
  Notes:
   n/a
  History:
   15-05-31
    fixed type error
  """
  #opts = read_struct(opts)
  #print opt
  
  for option in opts:
    if opt == int(option[0]):
      return option[1]

# ok
def get_group_desc(device, skip, sb):
  """Return an array of parsed block group descriptors.
  
  Created:
   15-06-01
  Last Modified:
   n/a
   
  Params:
   device - Device/image to read from.
   skip - LBA to superblock
  Return:
   Array of parsed bgds.
  
  Notes:
   15-06-01
    This struct may be either 32 or 64 bytes long.
    Need to find how to calculate values using dd and sb block sizes, etc [BUGFIX1]
  History:
   n/a
  """
  #sb = get_superblock(device, skip)
  block_size = get_struct_value(sb, "s_log_block_size")
  flex_bg = get_struct_value(sb, "s_log_groups_per_flex")  # gives # of bgd
  bgd_file = "ext4_group_desc_32.struct"
  bgd_size = 32
  
  if get_struct_value(sb, "s_desc_size") > 32 and get_struct_value(sb, "s_feature_incompat").count("|INCOMPAT_64BIT|") != 0:
    bgd_file = "ext4_group_desc_64.struct"
  bgd_loc = block_size / DD_BS  # points to block after sb block
  bgd_loc += skip - 2  # BUGFIX1: take offset into first block from calculation
  #bgd_size = bgd_size * flex_bg / DD_BS
  bgd = dump_parse(dd_read(device, bgd_size * flex_bg / DD_BS, bgd_loc), 
		   file_read(bgd_file), bgd_size, flex_bg)
  b = []
  non_ints = [6, 11]
  
  for arr in range(flex_bg):
    for num in range(12):
      # convert strings to ints
      if non_ints.count(num) != 0:
	# skip non-ints
	continue
      #print arr, num, bgd[num][2], bgd[num][3]
      bgd[num+arr*12][3] = int(bgd[num+arr*12][3])
    bgd[6+arr*12][3] = read_flags(bgd[6+arr*12][3], read_struct("bg_flags.flags"))
    b.append(bgd[arr*12:arr*12+12])
  return b

def get_inode(device, skip, i_num=[11]):
  """Reads inode tables.
  
  Created:
   15-06-01
  Last Modified:
   15-06-03
   
  Params:
   device - Device/image.
   skip - Starting block.
   i_num - Array of inode numbers to return.
  Return:
   Array of inodes.
  
  Notes:
   15-06-02
    Code takes way too long to read a single inode table (or am I doing something wrong?). 
     Need to break it into chunks or find a more efficient method...
   15-06-03
    Should skip processing empty inodes. Can use inode bitmap or check dump.
    Change func to return a single or group of inodes, not the table(s).
    Should store sb and bgd in a global var to prevent repeated loading on multiple calls.
  History:
   15-06-03
    Reduced processing time by returning an i_table subset.
  """
  sb = get_superblock(device, skip)
  bgd = get_group_desc(device, skip, sb)
  block_size = get_struct_value(sb, "s_log_block_size")
  #flex_bg = get_struct_value(sb, "s_log_groups_per_flex")
  i_file = "ext4_inode.struct"
  it_loc = get_struct_value(bgd[0], "bg_inode_table_lo") * (block_size / DD_BS)
  #it_size = (get_struct_value(bgd[1], "bg_inode_table_lo") * (block_size / DD_BS)) - it_loc
  i_size = get_struct_value(sb, "s_inode_size")
  it_size = get_struct_value(sb, "s_inodes_per_group")
  flex_bg = get_struct_value(sb, "s_log_groups_per_flex")
  it = []
  
  for num in i_num:
    if num < 1:
      # skip invalid inode #s
      continue
    index = (num - 1) % it_size
    blk_num = (num - 1) / it_size
    flex_grp = 0 # calculate the inode's flex group
    loc = (num / 2) + (num % 2)
    inode = dump_parse(dd_read(device, 1, it_loc + inc), file_read(i_file), i_size, 2)
  
  for inc in range(it_size):
    inode = dump_parse(dd_read(device, 1, it_loc + inc), file_read(i_file), i_size, 2)
  #it = dump_parse(dd_read(device, it_size / 2, it_loc), file_read(i_file), i_size, it_size)  # !!!
  #return dd_read(device, it_size / 2, it_loc)
    non_ints = [0, 1, 7, 10, 11, 12, 17, 26]
  
    for fld in range(26):
      if non_ints.count(fld) != 0:
        continue
      #print fld, inode[fld][3]
      inode[fld][3] = int(inode[fld][3])
    inode[0][3] = read_flags(inode[0][3], read_struct("i_mode.flags"))
    inode[3][3] = secs_to_dtime(inode[3][3])
    inode[4][3] = secs_to_dtime(inode[4][3])
    inode[5][3] = secs_to_dtime(inode[5][3])
    inode[6][3] = secs_to_dtime(inode[3][3])  # ternary conditional
    inode[10][3] = read_flags(inode[10][3], read_struct("i_flags.flags"))
    inode[23][3] = secs_to_dtime(inode[23][3])
    it.append(inode)
    #print inode
  return it
  
### Tests
#print grep_srch(dd_read("/dev/sdb", 4), "sys")
#print base_conv("88")
#print hex_conv("00 00 00 10")
#print type_to_size("le64[4]")
#print dump_parse(dd_read("/media/skeledrew/Seagate\ Expansion\ Drive/1tb/15-04-06.img", 2, 974397458), file_read("ext4_super_block.struct"))
#print dump_parse(dd_read("/dev/sda", 2, 974397458), "0054 le32 s_first_ino")[0][3].strip("\n")
#print pretty_parse("/media/skeledrew/Seagate\ Expansion\ Drive/250gb/sb_15-05-25_08-17.txt", "ext4_super_block.struct")
#print pretty_parse("/media/skeledrew/Seagate\ Expansion\ Drive/1tb/15-04-06.img", "ext4_super_block.struct", "", 974397458)
#print pretty_parse("/dev/sda2", ["ext4_group_desc_32.struct", 32, 16], "250gb-p2-gdt-8.txt", 8)
#print pretty_parse("/dev/sda2", ["ext4_group_desc_32.struct", 32, 1], "", 8)
#print pretty_parse("/dev/sda2", ["ext4_inode.struct", 256, 20], "250gb-p2-inode-8456.txt", 8456, 10)
#print get_superblock("/dev/sda2", 2)
#print get_struct_value(dump_parse(dd_read("/dev/sda2", 2, 2), file_read("ext4_super_block.struct")), "s_log_block_size")
#print secs_to_dtime(get_struct_value(get_superblock("/dev/sda2", 2), "s_mtime"))
#print read_flags(get_struct_value(get_superblock("/dev/sda2", 2), "s_state"), read_struct("s_state.flags"))
#print read_opt(get_struct_value(get_superblock("/dev/sda2", 2), "s_errors"), read_struct("s_errors.opts"))
#print get_group_desc("/dev/sda2", 2, get_superblock("/dev/sda2", 2))
print get_inode("/dev/sda2", 2)

### Notes:
# Error caused by unimplemented checkpoint
# Investigate error caused by extra space after name that caused value to be OK if printed alone or in array, but gave nothing if printed via a 'for' loop. Can probably fix by stripping spacess from input
# need to fix u32 data size issues


### Main

#unknown_struct1_print("/dev/sdb", 1310724104, 2, file_read("/isodevice/recovery/ext4_group_desc-32.struct"))

choice = 1  # check

while choice == 0:
  print "What would you like to do?"
  print "[1] Run a system command."
  print "[2] Raw read a file/device."
  print "[3] Search for a pattern using grep."
  
