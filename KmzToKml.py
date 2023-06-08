import os, sys
import zipfile

from pathlib import Path

class KmzToKml:

    def KmzConverter(self, path):

        self.directory_path = os.path.dirname(path)
        self.directory_path_2 = os.path.dirname(self.directory_path)  # Upper path
        self.base_file, self.ext = os.path.splitext(path)  # Lets us divide between the root filename and its extension
        self.path_base_file = self.base_file.split("/")
        self.file = self.path_base_file[-1]  # File name
        print("PATH: ", self.base_file, self.ext)

        if self.ext == ".kmz":

            # Step 1 is to convert .kmz to .zip

            self.filename = self.base_file + self.ext

            self.new_filename = self.base_file + ".zip"

            #print(self.filename, self.new_filename)
            os.rename(self.filename,
                      self.new_filename)  # If extension is .kmz it changes the extension to .zip; os.rename(src, dst). Also the path has to be given to the function

            # Step 2 is to unzip the folder

            with zipfile.ZipFile(self.new_filename, 'r') as archive:
                archive.extractall(
                    self.directory_path)  # Extracted file will be saves in the indicated path; extractall('path/dest_folder')
                # print(f'Done {self.new_filename.stem}')

            # Step 3 remove the remaining zip folder
            os.remove(self.new_filename)

            # Step 4 rename file with the original file name
            for filename in os.listdir(self.directory_path):
                self.base_file, self.ext = os.path.splitext(
                    filename)  # Lets us divide between the root filename and its extension

            if self.ext == ".kml":
                self.new_filename = self.directory_path + "/" + self.file + self.ext
                # print("NEW name: ", self.new_filename)
                self.old_filename = self.directory_path + "/doc" + self.ext
                # print("OLD name: ", self.old_filename)
                os.rename(self.old_filename,
                          self.new_filename)  # If extension is .kmz it changes the extension to .zip; os.rename(src, dst)
                # Also the path has to be given to the function
                return self.new_filename

        elif self.ext == ".kml":
            return path

        else:
            return -1  # return error

