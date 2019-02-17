import youtube_dl as y
from platform import system
import os
from moviepy import editor as mPy
import csv
# from moviepy.audio.io.AudioFileClip import AudioFileClip


class MediaHandler:
    def __init__(self, dir=r'C:\Users\patru\Desktop\video'):

        # change dir
        if (dir is not None) and os.getcwd() != dir:
            os.chdir(dir)
        # name of OS
        self.platform = system()

        self.video_dir = 'video_dir'
        self.audio_dir = 'audio_dir'
        if not os.path.isdir(self.video_dir):
            os.mkdir(self.video_dir)
        if not os.path.isdir(self.audio_dir):
            os.mkdir(self.audio_dir)

        self.video_filename = 'video.csv'

    def add_video(self, urls_list, convert_list, m='w'):
        assert len(urls_list) == len(convert_list), 'len urls and convert must be same'

        try:
            with open(self.video_filename, mode=m) as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                if os.stat(self.video_filename).st_size == 0:
                    writer.writerow(['url', 'convert'])

                for i in range(len(urls_list)):
                    # delete whitespaces
                    url, convert = urls_list[i].strip(), convert_list[i]
                    writer.writerow([url, convert])

        except Exception as e:
            print('exception at writing csv into file: \n{}'.format(e))

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

    def down_and_convert(self):
        urls = []
        convert_list = []
        try:
            with open(self.video_filename, newline='\n') as file:
                csv_reader = csv.reader(file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        print(f'Column names are {", ".join(row)}')
                        line_count += 1
                    else:
                        urls.append(row[0])
                        convert_list.append(row[1])
                        line_count += 1
                print(f'Processed {line_count-1} lines.')

        except Exception as e:
            print(f'exception at reading csv file: \n{e}\n\n')

        if urls is None:
            print('no urls inside')
            return
        else:
            info_dict = {url: convert for url, convert in zip(urls, convert_list)}
            bug_dict = {}
        try:
            for url, convert in zip(info_dict.keys(), info_dict.values()):
                self._down_video(url=url, convert=convert)
                bug_dict[url] = convert
        except Exception as e:
            print(f'exception at youtube downloader: \n{e}\n\n')
            # write into file others url
            all(info_dict.pop(k) for k in bug_dict.keys())

            urls = list(info_dict.keys())
            convert_list = list(info_dict.values())
            self.add_video(urls_list=urls, convert_list=convert_list, m='w')

    @staticmethod
    def mp4_to_mp3(name):
        clip = None
        try:
            # audio = AudioFileClip('{}.mp4'.format(name), buffersize=200000, fps=44100, nbytes=2)
            clip = mPy.VideoFileClip('{}.mp4'.format(name))
            clip.audio.write_audiofile('{}.mp3'.format(name))
        except Exception as e:
            print('exception at converting mp4 to mp3: \n{}'.format(e))
        finally:
            del clip


if __name__ == '__main__':
    h = MediaHandler()
    h.add_video(['https://www.youtube.com/watch?v=6U8Q39zkDXg&ut=', 'https://d3c33hcgiwev3.cloudfront.net/llHpclXaEeWg'
                                                                    'gQoi8-Beiw.processed/full/540p/index.mp4?Expires='
                                                                    '1550448000&Signature=ZnF6vSX2AZtPvyw3aRSgVm~S9sIK'
                                                                    'o4F4e0EcfUY54KUyRczlXCwoVjL54f~aW4OqYT8~2tcDT3yQm'
                                                                    'zLBraLheANMtMqJ0V2CEbf9ciz46m9rJOksNOBGbH1JTpVd7~'
                                                                    'KZk4pltI873HVSCvSEmGRcslB~hA7A4UH6stlKgcccrdM_&Key'
                                                                    '-Pair-Id=APKAJLTNE6QMUY6HBC5A'], [False], m='w')
    h.down_and_convert()
