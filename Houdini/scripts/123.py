
hou.setFps(25)
hou.playbar.setTimeRange(40,50)
hou.playbar.setPlaybackRange(1001,2000)
hou.setFrame(1001)

  


def create_camera():
    cam = hou.node("/obj").createNode("cam", "gl_cam")
    cam.setParms({"resx": 1920, "resy": 1080, "far":10000000})
    cam.setDisplayFlag(False)

def main():
    create_camera()

main()

