#! /bin/python

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

"""Raw Reader.
  
  Created:
   15-05-23
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
    - flags mapper
    - read extent tree
  History:
   n/a
"""

### Constants:
DEBUG = True

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

# convert bases using bc. ok
def base_conv(value, src_base="16", dst_base="A"):
  res = sys_call("echo 'ibase=" + src_base + ";obase=" + dst_base + ";" + value.upper() + "' | bc")
  if DEBUG and res == "":
    print "base_conv:", value
  return res

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
    print "hex_conv:", size, hex_data
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
def dump_parse(hex_data, params="00 char[8] unknown", struct_size=1024, struct_rpt=1):
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
  hex_data = string.split(hex_data, "\n")
  params = string.split(params, "\n")
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
	element = a_data[start:stop]
      
      elif size[2] == "byte":
	element = ""
	for d in data[start:stop]:
	  element += d + " "
	element.strip(' ')
	  
      else:
	element = hex_conv(data[start:stop], size)
      
      if DEBUG and element == "":
	line.append("dump_parse error!")
	print "dump_parse:", data[start:stop]
      line.append(element)
      hex_parse.append(line)
  return hex_parse
    
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
def offset_to_block(offset, fix=0, size=512):
  """Convert hex offset to lba?
  
  Created:
   14-07-??
  Last Modified:
   15-05-24
   
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
#print pretty_parse("/dev/sda2", ["ext4_group_desc_32.struct", 32, 16], "", 8)
print pretty_parse("/dev/sda2", ["ext4_inode.struct", 256, 20], "250gb-p2-inode-8456.txt", 8456, 10)


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
  
