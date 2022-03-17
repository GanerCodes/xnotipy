#!/usr/bin/python 
from os import environ
from os.path import expanduser, realpath, join as path_join, split as path_split
from subprocess import PIPE, Popen
from random import randint

Xresources_loc = expanduser("~/.Xresources")

class Notification:
    XNOTIFY_LOCATION = Popen(["which", "xnotify"], stdout = PIPE).stdout.read().decode().strip()
    RESOURCE_FILE_NAME = path_join(path_split(realpath(__file__))[0], "resources")
    __para_inline__ = {
        "IMG": "image",
        "TAG": "tag",
        "CMD": "cmd",
        "BAR": "bar",
        "SEC": ("time", 5)
    }
    __para_resource__ = {
        "background": ("background_color", "#000000"),
        "foreground": ("foreground_color", "#FFFFFF"),
        "border": ("border_color", "#FFFFFF"),
        "borderWidth": ("border_width", "1px"),
        "shrink": ("shrink", True),
        "title.font": "title_font",
        "body.font": "body_font",
        "wrap": ("text_wrap", True),
        "leading": "line_spacing",
        "alignment": ("text_alignment", "center"),
        "alignTop": "text_top_align",
        "padding": "padding",
        "maxHeight": "max_height",
        "gap": "gap",
        "imageWidth": "image_width",
        "geometry": "geometry",
        "gravity": ("base_location", "NE")
    }
    all_options = __para_inline__ | __para_resource__
    
    def get_name(self, x):
        return x[0] if isinstance(x, tuple) else x
    def get_value(self, x):
        return x[1] if isinstance(x, tuple) else None
    
    def __init__(self, text="", cmd=None, mouse_button=1, monitor=0, **para):
        self.mapping = {k: self.get_name(v) for k, v in self.all_options.items()}
        self.inverse_mapping = {v: k for k, v in self.mapping.items()}
        
        self.para = {
            v: self.get_value(self.all_options[k]) for k, v in self.mapping.items()
        } | para
        
        if self.para["tag"] is None:
            self.para["tag"] = str(randint(10 ** 8, 10 ** 10))
    
        if isinstance(t := self.para["geometry"], tuple|list):
            self.para["geometry"] = "{}x{}{:+}{:+}".format(
                t[0], t[1],
                t[2] if len(t) > 2 else 0,
                t[3] if len(t) > 3 else 0
            )
        
        if cmd:
            self.para["cmd"] = "1"
        
        self.mouse_button = mouse_button
        self.has_set_resources = False
        self.monitor = monitor
        self.text = text
        self.cmd = cmd
    
    def update_resources(self):
        with open(self.RESOURCE_FILE_NAME, "w") as f:
            for k, v in self.para.items():
                m = self.inverse_mapping[k]
                if v is None or not m in self.__para_resource__:
                    continue
                if isinstance(v, bool):
                    v = str(v).lower()
                f.write(f"xnotify.{m}: {v}\n")
        
        Popen(["xrdb", Xresources_loc, "-merge", self.RESOURCE_FILE_NAME]).wait()
    
    def activate(self, force_refresh_resources = False):
        if not self.has_set_resources or force_refresh_resources:
            self.update_resources()
            self.has_set_resources = True
        
        content = ""
        for k in self.__para_inline__.keys():
            if (m := self.para[self.mapping[k]]) is None:
                continue
            content += f"{k}:{m}\t"
            
        content += f"{self.text}"
        
        proc = Popen(
            [self.XNOTIFY_LOCATION, '-b', str(self.mouse_button), '-m', str(self.monitor)],
            stdin=PIPE, stdout=PIPE, env=environ
        )
        if proc.communicate(content.encode())[0].decode().strip():
            if isinstance(self.cmd, Notification):
                self.cmd.activate()
            elif isinstance(self.cmd, str|list|tuple):
                Popen(self.cmd)
            elif callable(self.cmd):
                self.cmd()
        

if __name__ == "__main__":
    n = Notification(
        "THE",
        geometry = (52, 5, -25, 25),
        shrink = False,
        border_width = 1,
        image = "/home/ganer/Media/Image/hehe/4419826351_1647281775807.png",
        cmd = Notification(
            "hey",
            cmd = ["chromium", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"]
        ),
    )
    n.activate()