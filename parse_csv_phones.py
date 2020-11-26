#!/usr/bin/env python3
from collections import Counter
import sys
import csv
import re

def parse_sms_file(file_path, output_file=sys.stdout):
    print(f"Starting parse of file for SMS {file_path}")
    ph_nos=[]
    with open(file_path, newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter='|', quotechar=' ')
      for row in spamreader:
          if (len(row)>3):
              x = re.search(r"\d{3}\.\d{3}\.\d{4}", row[3])
              if x:
                  ph_nos.append(x.group())
      print("Number   |  Count ") 
      for x,y in sorted(Counter(ph_nos).items(), key=lambda item: item[1], reverse=True):
          print(x, y)

def parse_phone_file(file_path, output_file=sys.stdout):
    print(f"Starting parse of file with phone numbers {file_path}")
    ans={}
    with open(file_path, newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter='|', quotechar=' ')
      for row in spamreader:
          if (len(row)>3):
              x = re.search(r"\d{3}\.\d{3}\.\d{4}", row[3])
              if x:
                  ph_no = x.group()
                  minutes = int(row[6])
                  ans[ph_no] = ans.get(ph_no,0) + minutes
      print("Number | Minutes")
      for x,y in sorted(ans.items(), key=lambda item: item[1], reverse=True):
          print(x, y)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("######## USAGE #######")
        print("./parse_csv_phones.py <file_name> phone|sms")
        sys.exit(2)
    if (sys.argv[2]=='sms'):
        parse_sms_file(sys.argv[1])
        sys.exit(0)
    elif (sys.argv[2]=='phone'):
        parse_phone_file(sys.argv[1])
        sys.exit(0)
    else:
        print("Invalid arg. Use either phone or sms")
