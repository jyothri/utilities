#!/usr/bin/env python3
from collections import Counter
from datetime import datetime
import sys
import csv
import re
import os


class Result:

  def __init__(self, phone):
    self.phone = phone  # The phone no. for which this data belongs to
    self.sms = {}  # The phoneNo-Count mapping made from this phone
    self.call = {}  # The phoneNo-minutes mapping made from this phone
    self.call_dates = []

  def add_sms(self, ph_no):
    if re.search(r"\d{3}.*\d{3}.*\d{4}", ph_no):
      self.sms[ph_no] = self.sms.get(ph_no, 0) + 1

  def add_minutes(self, ph_no, call_date, minute):
    self.call[ph_no] = self.call.get(ph_no, 0) + minute
    self.call_dates.append(call_date)

  def get_output(self):
    output = ""
    output += f"####### Analysis for {self.phone} ########\n"
    output += (f"####### From period "
               f"{self.call_dates[0] if self.call_dates else 'Unknown'} to "
               f"{self.call_dates[-1] if self.call_dates else 'Unknown'} "
               f"########\n")
    output += "####### ####### ####### ####### ########\n"

    output += " \n SMS Info \n"
    output += " \tPhone Number\t\tCount\n"
    for x, y in sorted(
        Counter(self.sms).items(), key=lambda item: item[1], reverse=True):
      output += f"\t{x}\t\t{y}\n"

    output += " \n Phone Info \n"
    output += " \tPhone Number\t\tMinutes\n"
    for x, y in sorted(
        Counter(self.call).items(), key=lambda item: item[1], reverse=True):
      output += f"\t{x}\t\t{y}\n"

    output += "\n####### ####### ####### ####### ########\n"
    return output


class PhoneDirectoryParser:

  def __init__(self, dir_path):
    self.dir_path = dir_path

  def process_dir(self):
    if not os.path.isdir(self.dir_path):
      print(f"Not a valid directory or no permissions {self.dir_path}")
      return

    if not os.path.exists("output"):
      os.makedirs("output")
    for file in os.listdir(self.dir_path):
      if file.endswith(".csv"):
        print(f"Processing {file}")
        out_file = "./output/" + os.path.splitext(file)[0] + ".log"
        print("Writing results to ", out_file)
        file_parser = PhoneFileParser("w", out_file)
        file_parser.parse_file(file)


class PhoneFileParser:

  def __init__(self, file_mode=None, out_file=None):
    if out_file:
      self.out_file = out_file
    else:
      self.out_file = datetime.now().strftime("results_%Y_%m_%d_%H_%M_%S.log")
    self.constants = self.known_constants()
    self.file_mode = "a"

  def known_constants(self):
    return {
        "AT&T", "SDDV=Plan minutes", "SDDV=Shared Minutes",
        "WIFI=Call over Wi-Fi", "NBSY=NumberSync",
        "MPSDG4=MobileShare Value 45GB", "MPSDG4=Mobile Share Value 45GB",
        "UNLMSG=Plan messages", "UNLMSG=Shared Messaging",
        "MPSDG3=Promo for Mobile Share Value 30GB with Rollover Data",
        "MPSDG3=Promofor Mobile Share Value 30GB with Rollover Data", ""
    }

  def parse_file(self, file_path):
    if not os.path.isfile(file_path):
      print(f"Not a valid file or no permissions {file_path}")
      return
    print(f"Starting parse of file {file_path}")
    result = None
    phone = None
    with open(file_path, newline="\n") as csvfile:
      spamreader = csv.reader(csvfile, delimiter=",", quotechar=" ")
      for row in spamreader:
        if not row:
          continue

        if len(row) == 1:
          # If we get some of the constants which are unknown
          # this app may not recognize. specifically , checks such
          # as SDDV for calls, SMS for sms.
          if row[0].strip() not in self.known_constants():
            print("Unknown", row[0].strip())

        if (len(row) == 2 and row[0] == "CALL DETAIL"):
          self.finish_processing(result)
          phone = row[1]
          result = Result(phone)

        if (len(row) == 2 and row[0].strip() == "DATADETAIL"):
          if phone != row[1]:
            # If SMS / Data detail is not same as phone detail,
            # finish processing current file and start new.
            self.finish_processing(result)
            phone = row[1]
            result = Result(phone)

        if (len(row) == 13 and row[7].strip() in ("SDDV", "WIFI", "NBSY")):
          result.add_minutes(row[4].strip(), row[2], int(row[6]))

        if (len(row) == 12 and row[9].strip() == "SMS"):
          result.add_sms(row[4].strip())

    self.finish_processing(result)

  def finish_processing(self, result):
    if not result:
      return

    print(f"Writing output to {self.out_file} for phone: {result.phone}")
    with open(self.out_file, self.file_mode) as f:
      f.write(result.get_output())


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Invalid number of arguments.")
    print("Usage: command <dir_path | file_path>")
    sys.exit(-1)

  input_path = sys.argv[1]

  if os.path.isdir(input_path):
    directoryParser = PhoneDirectoryParser(input_path)
    directoryParser.process_dir()
  elif os.path.isfile(input_path):
    PhoneFileParser().parse_file(input_path)
