#!/usr/bin/env python

def get_section(line):
    return line[1:-1]

def split_key_value(line):
    key,s,value = line.rpartition("=")
    return key,value

with open('/etc/nae/nae.conf') as f:
    for line in f:
        line = line.rstrip()
	if not line:
	    continue
	if line[0] == '[':
	    section = get_section(line)
            print section

	elif line[0] in '#;':
	    print 'comment'
	else:
	    key,value = split_key_value(line)
	    print key,value
	    
    
