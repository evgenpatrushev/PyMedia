import threading, time


def imp_def(result, event):
    import download_handler as dl
    result.append(dl)
    time.sleep(25)
    event.clear()


def help_list():
    """
    help function with func list
    video function list: # all means url of video
        # in the list
        add-video
        delete_video
        edit_video
        list_videos
    audio function list: # all means url or direction of video
        # in the list
        add-audio
        delete_audio
        edit_audio
        list_audios
        
    telegram function list:
        download media yourself

    :return:
    """
    pass


def video_function():
    pass


def audio_function():
    pass


def down_dots(event):
    while event.is_set():
        print('.', end='')
        time.sleep(0.5)


if __name__ == '__main__':
    lib = []
    signal = threading.Event()
    signal.set()
    imp_thread = threading.Thread(target=imp_def, name='imp_thread', args=(lib, signal))
    dots_thread = threading.Thread(target=down_dots, name='dots_thread', args=(signal,))
    l = threading.Lock()

    print("Hi, you run PyMedia :)")
    print("Right now I'm importing need libraries, please wait")
    dots_thread.start()
    imp_thread.start()
    dots_thread.join()
    imp_thread.join()
    dl = lib[0]

    print('\nOk. Importing done')
