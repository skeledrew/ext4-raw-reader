# ext4-raw-reader
A python script to read the raw contents of devices or their images for recovery, etc.

The Story:
After accidentally starting an OS install last year on a EXT4-formatted FS, I have been seeking a way to recover my data. Many of the tools I was able to find that could manage EXT4 partitions did not work very well since the partition table was lost. I knew my data was still there since the process only happened for a couple seconds and my /home was on a second partition. I decided to research the file system and create a script to read it's contents, with the ultimate aim of recovering my data.
