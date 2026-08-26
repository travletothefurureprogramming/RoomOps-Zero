import pyvolume

def set_volume(percent):
    try:
        pyvolume.custom(percent)
    except:
        print("Cant maximize the volume!")