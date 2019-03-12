import youtube_dl as y
from platform import system
import os
import re
from moviepy import editor as mPy
import logging
import csv


# from moviepy.audio.io.AudioFileClip import AudioFileClip


class MediaHandler:
    def __init__(self, dir=r'C:\Users\patru\Desktop\video'):

        # change dir
        if (dir is not None) and os.getcwd() != dir:
            os.chdir(dir)
            self.dir = dir
        # name of OS
        self.platform = system()

        self.video_dir = 'video_dir'
        self.audio_dir = 'audio_dir'
        if not os.path.isdir(self.video_dir):
            os.mkdir(self.video_dir)
        if not os.path.isdir(self.audio_dir):
            os.mkdir(self.audio_dir)

        self.video_filename = 'video.csv'

        # config logging system
        LOG_FORMAT = "%(level_name)s: %(message)s; at %(asctime)s"
        logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format=LOG_FORMAT)
        self.logger = logging.getLogger()

    def add_video(self, urls_list, convert_list, name_list, m='w'):
        try:
            if(len(urls_list) != len(convert_list)) or (len(urls_list) == len(name_list)):
                self.logger.error("exception at writing csv into file: \nHave to use same length of urls_list,"
                                  "convert_list anf name_list")
                return -1

            with open(self.video_filename, mode=m) as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                if os.stat(self.video_filename).st_size == 0:
                    writer.writerow(['url', 'convert', 'name'])

                for i in range(len(urls_list)):
                    # delete whitespaces
                    if (urls_list[i] != 'Nan' and name_list[i] != 'Nan') \
                            or (urls_list[i] == 'Nan' and name_list[i] == 'Nan'):
                        print(f"url={urls_list[i]} & video name={name_list[i]} will not be add into list"
                              "\nYou can't add url and video name with same type of value")
                        continue
                    url, convert, name = urls_list[i], convert_list[i], name_list[i]
                    writer.writerow([url, convert, name])
        except Exception as e:
            self.logger.error(f'exception at writing csv into file: \n{e}\n\n')
            return -1
        return 0

    def _down_video(self, url, convert=False):
        try:
            with y.YoutubeDL({}) as dl:
                os.chdir(self.video_dir)
                video_info = dl.extract_info(url=url, download=True)
                os.chdir('..')

                if convert:
                    print(f'Download .mp3 for {video_info["title"]}')
                    # filename without .mp4
                    filename = dl.prepare_filename(info_dict=video_info)[:-4]
                    self.mp4_to_mp3(filename)
        except Exception as e:
            print(f'Exception at _down_video : \n{e}\n\n')
            return -1
        return 0

    def read_from_csv(self):
        # 3 columns at csv, so list inside data list
        data = [[], [], []]
        try:
            with open(self.video_filename, newline='\n') as file:
                csv_reader = csv.reader(file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        print(f'Column names are {", ".join(row)}')
                        line_count += 1
                    else:
                        data[0].append(row[0])
                        data[1].append(row[1])
                        data[2].append(row[2])
                        line_count += 1
                print(f'Processed {line_count - 1} lines.')

        except Exception as e:
            print(f'exception at reading csv file: \n{e}\n\n')
            return -1
        return data[0], data[1], data[2]

    @staticmethod
    def change_and_back(func, new_dir, params):
        # save old dir
        old_dir = os.getcwd()
        # change dir where exist file
        os.chdir(new_dir)
        # do function
        return_value = func(params)
        # change to old dir
        os.chdir(old_dir)

        return return_value

    def down_and_convert_all(self):

        # --Reading csv for data
        answer = self.read_from_csv()
        if answer == -1:
            print('stop excecution down_and_convert_all: error')
            return -1
        else:
            urls, convert_list, name_list = answer

        if urls is None:
            print('no urls inside')
            return

        # --Sorting data to lists and dict
        else:
            url_dict = {url: convert for url, convert in zip(urls, convert_list) if url != 'Nan'}
            name_conv = [name for name, convert in zip(name_list, convert_list) if (name != 'Nan' and
                                                                                    convert is not False)]
            # bug list for add csv in the end
            # first list for url, second for convert flag and third for video name
            bug_list = [[], [], []]

            # Function for inserting bug's files to bug list
            def bug_insert(exception, value1, value2, value3):
                if exception == -1:
                    bug_list[0].append(value1)
                    bug_list[1].append(value2)
                    bug_list[2].append(value3)

        # --Download videos and convert to mp3 for urls
        for url, convert in zip(url_dict.keys(), url_dict.values()):
            exc = self._down_video(url=url, convert=convert)
            bug_insert(exception=exc, value1=url, value2=convert, value3='Nan')

        # --Convert video from pc memory to mp3
        for name in name_conv:
            # Find root video and start converting
            root = self.find(video_name=name, path='.')

            if not root:
                print(f'Haven\'t find this file {name}')

            else:
                exc = self.change_and_back(func=self.mp4_to_mp3, params=name, new_dir=root)
                bug_insert(exception=exc, value1='Nan', value2=True, value3=name)

        # Write into csv files that haven't done through this down and convert def
        # note that all lists in bug_list have to have the same size ... but everything could be
        if bug_list[0] or bug_list[1] or bug_list[2]:
            self.add_video(urls_list=bug_list[0], convert_list=bug_list[1], name_list=bug_list[2], m='w')

    @staticmethod
    def find(video_name, path):

        if not re.search('.mp4$', video_name):
            video_name += '.mp4'

        for root, dirs, files in os.walk(path, topdown=False):
            if video_name in files:
                return root

        return False

    def mp4_to_mp3(self, name):
        clip = None
        try:
            clip = mPy.VideoFileClip('{}.mp4'.format(name))

            self.change_and_back(func=clip.audio.write_audiofile, params=f'{name}.mp3',
                                 new_dir=os.path.join(self.dir, self.audio_dir))

        except Exception as e:
            print('exception at converting mp4 to mp3: \n{}'.format(e))
            return -1
        finally:
            del clip
        return 0


if __name__ == '__main__':
    h = MediaHandler()
    path = h.find('index-index', '.')

    # h.add_video(['https://www.youtube.com/watch?v=6U8Q39zkDXg&ut=',
    #              'https://d3c33hcgiwev3.cloudfront.net/llHpclXaEeWg'
    #              'gQoi8-Beiw.processed/full/540p/index.mp4?Expires='
    #              '1550448000&Signature=ZnF6vSX2AZtPvyw3aRSgVm~S9sIK'
    #              'o4F4e0EcfUY54KUyRczlXCwoVjL54f~aW4OqYT8~2tcDT3yQm'
    #              'zLBraLheANMtMqJ0V2CEbf9ciz46m9rJOksNOBGbH1JTpVd7~'
    #              'KZk4pltI873HVSCvSEmGRcslB~hA7A4UH6stlKgcccrdM_&Key'
    #              '-Pair-Id=APKAJLTNE6QMUY6HBC5A',
    #              'Nan',
    #              'https://lol'], [False, True, True, False], ['Nan', 'Nan', 'index-index', 'Nan'], m='w')
    # h.down_and_convert_all()
