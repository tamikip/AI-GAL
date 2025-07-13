################################################################################
## 初始化
################################################################################

init offset = -1

default the_hover_button = ''



################################################################################
## 样式
################################################################################

style default:
    properties gui.text_properties()
    language gui.language

style input:
    properties gui.text_properties("input", accent=True)
    adjust_spacing False

style hyperlink_text:
    properties gui.text_properties("hyperlink", accent=True)
    hover_underline True

style gui_text:
    properties gui.text_properties("interface")


style button:
    properties gui.button_properties("button")

style button_text is gui_text:
    properties gui.text_properties("button")
    yalign 0.5


style label_text is gui_text:
    properties gui.text_properties("label", accent=True)

style prompt_text is gui_text:
    properties gui.text_properties("prompt")


style bar:
    ysize gui.bar_size
    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    ysize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize gui.scrollbar_size
    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    ysize gui.slider_size
    base_bar Frame("gui/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/slider/horizontal_[prefix_]thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"


style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)



################################################################################
## 游戏内屏幕
################################################################################


## 对话屏幕 ########################################################################
##
## 对话屏幕用于向用户显示对话。它需要两个参数，who 和 what，分别是叙述角色的名字
## 和所叙述的文本。（如果没有名字，参数 who 可以是 None。）
##
## 此屏幕必须创建一个 id 为 what 的文本可视控件，因为 Ren'Py 使用它来管理文本显
## 示。它还可以创建 id 为 who 和 id 为 window 的可视控件来应用样式属性。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#say

default say_window_alpha = 1.0
screen say(who, what):
    style_prefix "say"

    window:
        id "window"
        add '对话_对话框' xalign 0.5 alpha say_window_alpha

        if who is not None:

            window:
                id "namebox"
                style "namebox"
                text who:
                    id "who"
                    # offset(-36,2)
                    color "#4C3D3D"
                    outlines [(absolute(4), "#ffffff", absolute(0), absolute(0))]
                at transform:
                    alpha say_window_alpha

        text what id "what" xoffset -40


    ## 如果有对话框头像，会将其显示在文本之上。请不要在手机界面下显示这个，因为
    ## 没有空间。
    if not renpy.variant("small"):
        add SideImage() xalign 0.0 yalign 1.0


## 通过 Character 对象使名称框可用于样式化。
init python:
    config.character_id_prefixes.append('namebox')

style window is default
style say_label is default
style say_dialogue is default
style say_thought is say_dialogue

style namebox is default
style namebox_label is say_label


style window:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height

    # background Image("images/UI素材/对话/对话_对话框.png", xalign=0.5, yalign=0.0)

style namebox:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height

    background Image("images/UI素材/对话/对话_角色名框.png", xalign=0.5, yalign=0.5)
    # background Frame("images/UI素材/对话/对话_角色名框.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label:
    properties gui.text_properties("name", accent=True)
    xalign gui.name_xalign
    yalign 0.5

style say_dialogue:
    properties gui.text_properties("dialogue")

    xpos gui.dialogue_xpos
    xsize gui.dialogue_width
    ypos gui.dialogue_ypos

    adjust_spacing False

## 输入屏幕 ########################################################################
##
## 此屏幕用于显示 renpy.input。prompt 参数用于传递文本提示。
##
## 此屏幕必须创建一个 id 为 input 的输入可视控件来接受各种输入参数。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#input

screen input(prompt):
    style_prefix "input"

    window:
        add '对话_对话框' xalign 0.5 alpha say_window_alpha

        vbox:
            xanchor gui.dialogue_text_xalign
            xpos gui.dialogue_xpos
            xsize gui.dialogue_width
            ypos gui.dialogue_ypos

            text prompt style "input_prompt"
            input id "input"

style input_prompt is default

style input_prompt:
    xalign gui.dialogue_text_xalign  # 保持水平对齐方式（通常 left/center/right）
    xpos -60  # 向左移动 20 像素（负值向左，正值向右）
    ypos -20  # 向上移动 10 像素（负值向上，正值向下）
    properties gui.text_properties("input_prompt")  # 保留默认文本属性（如颜色、描边等）
    size 36  # 增大字体大小

style input:
    xalign gui.dialogue_text_xalign
    xmaximum gui.dialogue_width
    size 42



## 选择屏幕 ########################################################################
##
## 此屏幕用于显示由 menu 语句生成的游戏内选项。参数 items 是一个对象列表，每个对
## 象都有字幕和动作字段。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption:
                text_yoffset 14
                text_hover_yoffset 24
                text_outlines [(absolute(4), "#4C3D3D", absolute(0), absolute(0))]
                text_hover_outlines [(absolute(4), "#ffffff", absolute(0), absolute(0))]
                action i.action


style choice_vbox is vbox
style choice_button is button
style choice_button_text is button_text

style choice_vbox:
    xalign 0.5
    ypos 405
    yanchor 0.5

    spacing gui.choice_spacing

style choice_button is default:
    properties gui.button_properties("choice_button")

style choice_button_text is default:
    properties gui.text_properties("choice_button")


## 快捷菜单屏幕 ######################################################################
##
## 快捷菜单显示于游戏内，以便于访问游戏外的菜单。

screen quick_menu():

    ## 确保该菜单出现在其他屏幕之上，
    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            anchor(1.0,0.5)
            pos(1670,1010)
            spacing 22

            for button_name,the_action in {
            '隐藏':HideInterface(),
            '自动':Preference("auto-forward", "toggle"), 
            '快进':Skip(), 
            '历史':ShowMenu('history'),
            '快读':QuickLoad(), 
            '快存':QuickSave(), 
            '存档':ShowMenu('save'), 
            '设置':ShowMenu('preferences'), 
            '退出':MainMenu()}.items():
                button:
                    xycenter(0.5,0.5)
                    xysize(58,83)
                    if button_name == '快进':
                        alternate Skip(fast=True, confirm=True)

                    if the_hover_button == button_name or (button_name == '快进' and renpy.get_skipping()) or (button_name == '自动' and preferences.afm_enable == True):
                        add '对话_快捷菜单_焦点底图' xycenter(0.5,0.5)
                        text button_name:
                            size 16
                            color '#fff'
                            pos (-2,4)
                    
                    add '对话_快捷菜单_'+button_name xycenter(0.5,0.5)

                    hovered SetVariable('the_hover_button',button_name)
                    unhovered SetVariable('the_hover_button','')
                    action the_action

## 此代码确保只要用户没有主动隐藏界面，就会在游戏中显示 quick_menu 屏幕。
init python:
    config.overlay_screens.append("quick_menu")

default quick_menu = True

style quick_button is default
style quick_button_text is button_text

style quick_button:
    properties gui.button_properties("quick_button")

style quick_button_text:
    properties gui.text_properties("quick_button")


################################################################################
## 标题和游戏菜单屏幕
################################################################################

## 导航屏幕 ########################################################################
##
## 该屏幕包含在标题菜单和游戏菜单中，并提供导航到其他菜单，以及启动游戏。


screen navigation():

    # add 'images/UI预览/《AI-GAL》UI设计标题界面+对话界面+历史界面+确认框_画板 1.jpg' xycenter(0.5,0.5)

    # add '标题_背景' align(0.0,0.5)

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing gui.navigation_spacing

        for name,the_action in {
        '开始游戏' : Start(),
        '对话模式' : Start("talk_mode"),
        '读取存档' : ShowMenu("load"),
        '游戏设置' : ShowMenu("preferences"),
        '游戏帮助' : ShowMenu("about"),
        '退出游戏' : Quit(confirm=not main_menu)}.items():
            imagebutton:
                idle '标题_按钮_' + name + '_默认'
                hover '标题_按钮_' + name + '_焦点'
                action the_action


        # if main_menu:

        #     textbutton _("开始游戏") action Start()

        # else:

        #     textbutton _("历史") action ShowMenu("history")

        #     textbutton _("保存") action ShowMenu("save")

        # textbutton _("读取游戏") action ShowMenu("load")

        # textbutton _("设置") action ShowMenu("preferences")

        # if _in_replay:

        #     textbutton _("结束回放") action EndReplay(confirm=True)

        # elif not main_menu:

        #     textbutton _("标题菜单") action MainMenu()

        # textbutton _("关于") action ShowMenu("about")

        # if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):

        #     ## “帮助”对移动设备来说并非必需或相关。
        #     textbutton _("帮助") action ShowMenu("help")

        # if renpy.variant("pc"):

        #     ## 退出按钮在 iOS 上是被禁止使用的，在安卓和网页上也不是必要的。
        #     textbutton _("退出") action Quit(confirm=not main_menu)


style navigation_button is gui_button
style navigation_button_text is gui_button_text

style navigation_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")

style navigation_button_text:
    properties gui.text_properties("navigation_button")


## 标题菜单屏幕 ######################################################################
##
## 用于在 Ren'Py 启动时显示标题菜单。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#main-menu
init python:
    video_list = ["gui/custom/background.webm", "gui/custom/background1.webm",]
    selected_video = renpy.random.choice(video_list)

screen main_menu():

    ## 此语句可确保替换掉任何其他菜单屏幕。
    tag menu
    add Movie(play=selected_video, loop=True)

#     add gui.main_menu_background

    # ## 此空框可使标题菜单变暗。
    # frame:
    #     style "main_menu_frame"

    ## use 语句将其他的屏幕包含进此屏幕。标题屏幕的实际内容在导航屏幕中。
    use navigation

    # if gui.show_name:

    #     vbox:
    #         style "main_menu_vbox"

    #         text "[config.name!t]":
    #             style "main_menu_title"

    #         text "[config.version]":
    #             style "main_menu_version"


style main_menu_frame is empty
style main_menu_vbox is vbox
style main_menu_text is gui_text
style main_menu_title is main_menu_text
style main_menu_version is main_menu_text

style main_menu_frame:
    xsize 420
    yfill True

    # background "gui/overlay/main_menu.png"

style main_menu_vbox:
    xalign 1.0
    xoffset -30
    xmaximum 1200
    yalign 1.0
    yoffset -30

style main_menu_text:
    properties gui.text_properties("main_menu", accent=True)

style main_menu_title:
    properties gui.text_properties("title")

style main_menu_version:
    properties gui.text_properties("version")


## 游戏菜单屏幕 ######################################################################
##
## 此屏幕列出了游戏菜单的基本共同结构。可使用屏幕标题调用，并显示背景、标题和导
## 航菜单。
##
## scroll 参数可以是 None，也可以是 viewport 或 vpgrid。此屏幕旨在与一个或多个子
## 屏幕同时使用，这些子屏幕将被嵌入（放置）在其中。

screen game_menu(title, scroll=None, yinitial=0.0, spacing=0, background_image='淡蓝色'):

    if background_image == '淡蓝色':
        add '#F3FAFF'
    elif background_image == '透明黑色':
        add '#000000' alpha 0.5

    add '通用_界面_背景' xycenter(0.528,0.5)

    fixed:
        xycenter(0.105,0.18)
        xysize(120,220)
        add '通用_界面_标题框' xycenter(0.5,0.5) xysize(120,220)
        text title:
            xycenter(0.5,0.5)
            color '#ffffff'
            vertical True
            size 50
    
    imagebutton:
        xysize(170,120)
        xycenter(1740,940)
        idle 'images/UI素材/通用/通用_界面_按钮_退出.png'
        hover Fixed(
            'images/UI素材/通用/通用_界面_按钮说明底图.png',
            'images/UI素材/通用/通用_界面_按钮_退出.png',
            Text('退出', xycenter=(0.85,0.5), vertical=True, color='#ffffff', size=34),
            xysize=(170,120)
        )
        action Return()
    
    if title == '存档' and main_menu == False:
        imagebutton:
            xysize(170,120)
            xycenter(1740,790)
            idle 'images/UI素材/通用/通用_界面_按钮_读档.png'
            hover Fixed(
                'images/UI素材/通用/通用_界面_按钮说明底图.png',
                'images/UI素材/通用/通用_界面_按钮_读档.png',
                Text('读档', xycenter=(0.85,0.5), vertical=True, color='#ffffff', size=34),
                xysize=(170,120)
            )
            action ShowMenu('load')
    
    elif title == '读档' and main_menu == False:
        imagebutton:
            xysize(170,120)
            xycenter(1740,790)
            idle 'images/UI素材/通用/通用_界面_按钮_存档.png'
            hover Fixed(
                'images/UI素材/通用/通用_界面_按钮说明底图.png',
                'images/UI素材/通用/通用_界面_按钮_存档.png',
                Text('存档', xycenter=(0.85,0.5), vertical=True, color='#ffffff', size=34),
                xysize=(170,120)
            )
            action ShowMenu('save')


    # style_prefix "game_menu"

    # if main_menu:
    #     add gui.main_menu_background
    # else:
    #     add gui.game_menu_background

    # frame:
    #     style "game_menu_outer_frame"

    #     hbox:

    #         ## 导航部分的预留空间。
    #         frame:
    #             style "game_menu_navigation_frame"

    #         frame:
    #             style "game_menu_content_frame"

    #             if scroll == "viewport":

    #                 viewport:
    #                     yinitial yinitial
    #                     scrollbars "vertical"
    #                     mousewheel True
    #                     draggable True
    #                     pagekeys True

    #                     side_yfill True

    #                     vbox:
    #                         spacing spacing

    #                         transclude

    #             elif scroll == "vpgrid":

    #                 vpgrid:
    #                     cols 1
    #                     yinitial yinitial

    #                     scrollbars "vertical"
    #                     mousewheel True
    #                     draggable True
    #                     pagekeys True

    #                     side_yfill True

    #                     spacing spacing

    #                     transclude

    #             else:

    #                 transclude

    # use navigation

    # textbutton _("返回"):
    #     style "return_button"

    #     action Return()

    # if main_menu:
    #     key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty
style game_menu_navigation_frame is empty
style game_menu_content_frame is empty
style game_menu_viewport is gui_viewport
style game_menu_side is gui_side
style game_menu_scrollbar is gui_vscrollbar

style game_menu_label is gui_label
style game_menu_label_text is gui_label_text

style return_button is navigation_button
style return_button_text is navigation_button_text

style game_menu_outer_frame:
    bottom_padding 45
    top_padding 180

    # background "gui/overlay/game_menu.png"
    background '#F3FAFF'

style game_menu_navigation_frame:
    xsize 420
    yfill True

style game_menu_content_frame:
    left_margin 60
    right_margin 30
    top_margin 15

style game_menu_viewport:
    xsize 1380

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side:
    spacing 15

style game_menu_label:
    xpos 75
    ysize 180

style game_menu_label_text:
    size gui.title_text_size
    color gui.accent_color
    yalign 0.5

style return_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -45


## 关于屏幕 ########################################################################
##
## 此屏幕提供有关游戏和 Ren'Py 的制作人员和版权信息。
##
## 此屏幕没有什么特别之处，因此它也可以作为一个例子来说明如何制作一个自定义屏
## 幕。

screen about():

    tag menu

    use game_menu(_("关于"))

    ## 此 use 语句将 game_menu 屏幕包含到了这个屏幕内。子级 vbox 将包含在
    ## game_menu 屏幕的 viewport 内。
    # use game_menu(_("关于"), scroll="viewport"):

    viewport:
        id 'about_viewport'
        draggable True
        mousewheel True
        xysize(1300,786)
        pos(322,140)

        vbox:
            spacing 30
            
            label "[config.name!t]"
            text _("版本 [config.version!t]")

            ## gui.about 通常在 options.rpy 中设置。
            if gui.about:
                text "[gui.about!t]"

            text _("引擎：{a=https://www.renpy.org/}Ren'Py{/a} \n [renpy.version_only]")
            text '[renpy.license!t]'
    
    bar:
        xysize(36,604)
        pos(1695,242)
        value YScrollValue('about_viewport')

        bar_vertical True
        unscrollable "hide"
        bar_invert True
        
        base_bar '历史_滚动条'
        thumb '历史_滑块_默认'
        hover_thumb '历史_滑块_焦点'


style about_label is gui_label
style about_label_text is gui_label_text
style about_text is gui_text

style about_label_text:
    size gui.label_text_size


## 读取和保存屏幕 #####################################################################
##
## 这些屏幕负责让用户保存游戏并能够再次读取。由于它们几乎完全一样，因此这两个屏
## 幕都是以第三个屏幕 file_slots 来实现的。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#save https://doc.renpy.cn/zh-
## CN/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("存档"))


screen load():

    tag menu

    use file_slots(_("读档"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue(pattern=_("第 {} 页"), auto=_("自动存档"), quick=_("快速存档"))

    use game_menu(title)

    fixed:

        xycenter(0.5,0.52)

        ## 此代码确保输入控件在任意按钮执行前可以获取 enter 事件。
        order_reverse True

        ## 存档位网格。
        grid gui.file_slot_cols gui.file_slot_rows:
            # xysize(1600,900)
            # style_prefix "slot"

            xycenter(0.498,0.474)

            # spacing gui.slot_spacing
            xspacing 65
            yspacing 56

            for i in range(gui.file_slot_cols * gui.file_slot_rows):

                $ slot = i + 1

                button:

                    xysize(400,232)

                    hovered SetVariable('the_hover_button', FileSlotName(slot, 9))
                    unhovered SetVariable('the_hover_button', '')
                    action FileAction(slot)

                    
                    add FileScreenshot(slot, empty='存档_存档框_占位图')  xycenter(0.5,0.5)

                    if the_hover_button == FileSlotName(slot, 9):
                        add '存档_存档框_焦点' xycenter(0.5,0.5)
                    else:
                        add '存档_存档框_默认' xycenter(0.5,0.5)
                    
                    text FileTime(slot, format=_("{#file_time}%Y-%m-%d %H:%M"), empty=_("NO TIME LOGGED")):
                        if the_hover_button == FileSlotName(slot, 9):
                            color "#4C3D3D"
                        else:
                            color "#ffffff"
                        size 20
                        xycenter(0.74,0.94)

                    if len(FileSlotName(slot, 9)) == 1:
                        text 'NO-00' + FileSlotName(slot, 9):
                            xycenter(0.1,0.17)
                            size 22
                            if the_hover_button == FileSlotName(slot, 9):
                                color "#4C3D3D"
                            else:
                                color "#ffffff"
                            at transform:
                                rotate_pad True
                                rotate -45
                                
                    else:
                        text 'NO-0' + FileSlotName(slot, 9):
                            xycenter(0.1,0.17)
                            size 22
                            if the_hover_button == FileSlotName(slot, 9):
                                color "#4C3D3D"
                            else:
                                color "#ffffff"
                            at transform:
                                rotate_pad True
                                rotate -45

                    key "save_delete" action FileDelete(slot)

    vbox:
        
        anchor(0.5,0.0)
        pos(1710,125)
        spacing 10

        for page in range(1, 9):
            button:
                xysize(110,60)
                xycenter(0.5,0.5)

                if the_hover_button == page:
                    add '存档_页码按钮_焦点底图' xycenter(0.5,0.5)
                    text '选此':
                        vertical True
                        size 18
                        color "#ffffff"
                        xycenter(0.91,0.5)
                
                if isinstance(FileCurrentPage(), int) and page == int(FileCurrentPage()):
                    add '存档_页码按钮_已选底图' xycenter(0.5,0.5)
                    text '已选':
                        vertical True
                        size 18
                        color "#ffffff"
                        xycenter(0.13,0.5)

                add '存档_页码按钮_按钮' xycenter(0.5,0.5)
                text '[page]':
                    xycenter(0.508,0.5)
                    size 16
                    color "#ffffff"
                
                hovered SetVariable('the_hover_button', page)
                unhovered SetVariable('the_hover_button', '')
                action FilePage(page)

        # ## 用于访问其他页面的按钮。
        # vbox:
        #     style_prefix "page"

        #     xalign 0.5
        #     yalign 1.0

        #     hbox:
        #         xalign 0.5

        #         spacing gui.page_spacing

        #         textbutton _("<") action FilePagePrevious()
        #         key "save_page_prev" action FilePagePrevious()

        #         if config.has_autosave:
        #             textbutton _("{#auto_page}A") action FilePage("auto")

        #         if config.has_quicksave:
        #             textbutton _("{#quick_page}Q") action FilePage("quick")

        #         ## range(1, 10) 给出 1 到 9 之间的数字。
        #         for page in range(1, 10):
        #             textbutton "[page]" action FilePage(page)

        #         textbutton _(">") action FilePageNext()
        #         key "save_page_next" action FilePageNext()

        #     if config.has_sync:
        #         if CurrentScreenName() == "save":
        #             textbutton _("上传同步"):
        #                 action UploadSync()
        #                 xalign 0.5
        #         else:
        #             textbutton _("下载同步"):
        #                 action DownloadSync()
        #                 xalign 0.5


style page_label is gui_label
style page_label_text is gui_label_text
style page_button is gui_button
style page_button_text is gui_button_text

style slot_button is gui_button
style slot_button_text is gui_button_text
style slot_time_text is slot_button_text
style slot_name_text is slot_button_text

style page_label:
    xpadding 75
    ypadding 5

style page_label_text:
    textalign 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button:
    properties gui.button_properties("page_button")

style page_button_text:
    properties gui.text_properties("page_button")

style slot_button:
    properties gui.button_properties("slot_button")

style slot_button_text:
    properties gui.text_properties("slot_button")


## 设置屏幕 ########################################################################
##
## 设置屏幕允许用户配置游戏，使其更适合自己。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#preferences


screen preferences_button(title='', p1=['', NullAction()], p2=['', NullAction()], selected=0):
    fixed:
        xysize(615,90)
        hbox:
            spacing 18
            fixed:
                xycenter(0.5,0.5)
                xysize(320,90)
                add '设置_项目_标题框' xycenter(0.5,0.5)
                text title:
                    xycenter(0.5,0.5)
                    size 40
                    color '#ffffff'
            
            button:
                xysize(126,76)
                xycenter(0.5,0.5)
                
                if the_hover_button == title+'_'+p1[0]:
                    add '设置_项目_按钮_焦点' xycenter(0.5,0.5)
                elif selected == 1:
                    add '设置_项目_按钮_已选' xycenter(0.5,0.5)
                else:
                    add '设置_项目_按钮_未选' xycenter(0.5,0.5)

                text p1[0]:
                    size 30
                    color '#ffffff'
                    xycenter(0.5,0.3)
                hovered SetVariable('the_hover_button', title+'_'+p1[0])
                unhovered SetVariable('the_hover_button', '')
                action p1[1]
            
            button:
                xysize(126,76)
                xycenter(0.5,0.5)
                
                if the_hover_button == title+'_'+p2[0]:
                    add '设置_项目_按钮_焦点' xycenter(0.5,0.5)
                elif selected == 2:
                    add '设置_项目_按钮_已选' xycenter(0.5,0.5)
                else:
                    add '设置_项目_按钮_未选' xycenter(0.5,0.5)

                text p2[0]:
                    size 30
                    color '#ffffff'
                    xycenter(0.5,0.3)
                hovered SetVariable('the_hover_button', title+'_'+p2[0])
                unhovered SetVariable('the_hover_button', '')
                action p2[1]


screen preferences_bar(title='', the_action=NullAction(), current_value=0.5):
    fixed:
        xysize(615,90)
        hbox:
            spacing 18
            fixed:
                xycenter(0.5,0.5)
                xysize(320,90)
                add '设置_项目_标题框' xycenter(0.5,0.5)
                text title:
                    xycenter(0.5,0.5)
                    size 40
                    color '#ffffff'
            
            fixed:
                xycenter(0.5,0.5)
                xysize(266,90)
                vbox:
                    spacing 18
                    fixed:
                        xysize(266,31)
                        xycenter(0.5,0.5)
                        add '设置_项目_滑动项目信息显示底图' xycenter(0.5,0.5)
                        text 'MIN' xycenter(0.13,0.5) size 17 color '#fff'
                        text str(int(round(current_value,2)*100)) + '%' xycenter(0.5,0.5) size 20 color '#fff'
                        text 'MAX' xycenter(0.87,0.5) size 17 color '#fff'
                    
                    bar:
                        xysize(266,41)
                        xycenter(0.5,0.5)
                        left_gutter 8
                        right_gutter 8
                        thumb_offset 10
                        
                        bar_vertical False
                        bottom_bar '设置_项目_滚动条_未填充'
                        top_bar '设置_项目_滚动条_已填充'
                        thumb '设置_项目_滑块_默认'
                        hover_thumb '设置_项目_滑块_焦点'

                        value the_action

                        if title == '文本显示速度':
                            released Function(text_cps_preview.update_cps)

                        if title == '自动前进速度':
                            bar_invert True

default text_cps_preview = PreviewSlowText("这是一段测试文本显示速度的测试文本，一共会分为两行来完整显示……", color='#fff')
screen preferences():

    tag menu

    use game_menu(_("设置"))

    vbox:
        pos(344,175)
        spacing 70
        use preferences_button(
            '窗口显示模式', 
            ['全屏', Preference("display", "fullscreen")], 
            ['窗口', Preference("display", "window")],
            1 if preferences.fullscreen else 2
            )
        use preferences_button(
            '快进未读文本', 
            ['开启', Preference('skip', 'all')], 
            ['关闭', Preference('skip', 'seen')],
            1 if preferences.skip_unseen else 2
            )
        use preferences_button(
            '忽略界面转场', 
            ['开启', Preference('transitions', 'all')], 
            ['关闭', Preference('transitions', 'none')],
            1 if preferences.transitions else 2
            )
        use preferences_bar(
            '自动前进速度',
            Preference("auto-forward time", range=50),
            1-preferences.afm_time/50
        )
        use preferences_bar(
            '对话框透明度',
            VariableValue("say_window_alpha", range=1.0),
            say_window_alpha
        )
    
    vbox:
        pos(1050,175)
        spacing 70
        use preferences_bar(
            '总体声音音量',
            Preference('main volume'),
            preferences.get_mixer('main')
        )
        use preferences_bar(
            '音乐声音音量',
            Preference('music volume'),
            preferences.get_mixer('music')
        )
        use preferences_bar(
            '音效声音音量',
            Preference('sound volume'),
            preferences.get_mixer('sfx')
        )
        use preferences_bar(
            '文本显示速度',
            Preference('text speed'),
            1.0 if preferences.text_cps == 0 else preferences.text_cps/200
        )

        fixed:
            xysize(615,90)
            xycenter(0.5,0.5)
            add '设置_测试文本框' xycenter(0.5,0.5) xoffset 24

            fixed:
                xysize(500,70)
                xycenter(0.5,0.5) 
                add text_cps_preview:
                    yoffset 8
                    ysize 38
        

        # vbox:

        #     hbox:
        #         box_wrap True

        #         if renpy.variant("pc") or renpy.variant("web"):

        #             vbox:
        #                 style_prefix "radio"
        #                 label _("显示")
        #                 textbutton _("窗口") action Preference("display", "window")
        #                 textbutton _("全屏") action Preference("display", "fullscreen")

        #         vbox:
        #             style_prefix "check"
        #             label _("快进")
        #             textbutton _("未读文本") action Preference("skip", "toggle")
        #             textbutton _("选项后继续") action Preference("after choices", "toggle")
        #             textbutton _("忽略转场") action InvertSelected(Preference("transitions", "toggle"))

        #         ## 可在此处添加 radio_pref 或 check_pref 类型的额外 vbox，以添加
        #         ## 额外的创建者定义的偏好设置。

        #     null height (4 * gui.pref_spacing)

        #     hbox:
        #         style_prefix "slider"
        #         box_wrap True

        #         vbox:

        #             label _("文字速度")

        #             bar value Preference("text speed")

        #             label _("自动前进时间")

        #             bar value Preference("auto-forward time")

        #         vbox:

        #             if config.has_music:
        #                 label _("音乐音量")

        #                 hbox:
        #                     bar value Preference("music volume")

        #             if config.has_sound:

        #                 label _("音效音量")

        #                 hbox:
        #                     bar value Preference("sound volume")

        #                     if config.sample_sound:
        #                         textbutton _("测试") action Play("sound", config.sample_sound)


        #             if config.has_voice:
        #                 label _("语音音量")

        #                 hbox:
        #                     bar value Preference("voice volume")

        #                     if config.sample_voice:
        #                         textbutton _("测试") action Play("voice", config.sample_voice)

        #             if config.has_music or config.has_sound or config.has_voice:
        #                 null height gui.pref_spacing

        #                 textbutton _("全部静音"):
        #                     action Preference("all mute", "toggle")
        #                     style "mute_all_button"


style pref_label is gui_label
style pref_label_text is gui_label_text
style pref_vbox is vbox

style radio_label is pref_label
style radio_label_text is pref_label_text
style radio_button is gui_button
style radio_button_text is gui_button_text
style radio_vbox is pref_vbox

style check_label is pref_label
style check_label_text is pref_label_text
style check_button is gui_button
style check_button_text is gui_button_text
style check_vbox is pref_vbox

style slider_label is pref_label
style slider_label_text is pref_label_text
style slider_slider is gui_slider
style slider_button is gui_button
style slider_button_text is gui_button_text
style slider_pref_vbox is pref_vbox

style mute_all_button is check_button
style mute_all_button_text is check_button_text

style pref_label:
    top_margin gui.pref_spacing
    bottom_margin 3

style pref_label_text:
    yalign 1.0

style pref_vbox:
    xsize 338

style radio_vbox:
    spacing gui.pref_button_spacing

style radio_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/radio_[prefix_]foreground.png"

style radio_button_text:
    properties gui.text_properties("radio_button")

style check_vbox:
    spacing gui.pref_button_spacing

style check_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"

style check_button_text:
    properties gui.text_properties("check_button")

style slider_slider:
    xsize 525

style slider_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 15

style slider_button_text:
    properties gui.text_properties("slider_button")

style slider_vbox:
    xsize 675


## 历史屏幕 ########################################################################
##
## 这是一个向用户显示对话历史的屏幕。虽然此屏幕没有什么特别之处，但它必须访问储
## 存在 _history_list 中的对话历史记录。
##
## https://doc.renpy.cn/zh-CN/history.html

screen history():

    tag menu

    ## 避免预缓存此屏幕，因为它可能非常大。
    predict False

    use game_menu(_("历史"),background_image='透明黑色')

    if len(_history_list) > 0:
        viewport:
            id 'history_viewport'
            draggable True
            mousewheel True
            yinitial 1.0
            xysize(1300,786)
            pos(322,140)
            vbox:
                spacing 36
                for h in _history_list:
                    hbox:
                        if h.who:
                            fixed:
                                xysize (200,38)
                                text h.who:
                                    size 38
                                    if "color" in h.who_args:
                                        color h.who_args["color"]
                                    else:
                                        color '#000000'
                        else:
                            add Null(200,38)

                        
                        $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
                        text what:
                            line_spacing 9
                            color '#000000'
                            size 28
        
        bar:
            xysize(36,604)
            pos(1695,242)
            value YScrollValue('history_viewport')

            bar_vertical True
            unscrollable "hide"
            bar_invert True
            
            base_bar '历史_滚动条'
            thumb '历史_滑块_默认'
            hover_thumb '历史_滑块_焦点'

    else:
        fixed:
            xysize(1300,786)
            pos(322,140)
            text '尚无对话历史记录' xycenter(0.5,0.5)


                


    # for h in _history_list:

    #     window:

    #         ## 此代码可确保如果 history_height 为 None 时仍可正常显示条目。
    #         has fixed:
    #             yfit True

    #         if h.who:

    #             label h.who:
    #                 style "history_name"
    #                 substitute False

    #                 ## 从 Character 对象中获取叙述角色的文字颜色，如果设置了
    #                 ## 的话。
    #                 if "color" in h.who_args:
    #                     text_color h.who_args["color"]

    #         $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
    #         text what:
    #             substitute False

    # use game_menu(_("历史"), scroll=("vpgrid" if gui.history_height else "viewport"), yinitial=1.0, spacing=gui.history_spacing):

    #     style_prefix "history"

    #     for h in _history_list:

    #         window:

    #             ## 此代码可确保如果 history_height 为 None 时仍可正常显示条目。
    #             has fixed:
    #                 yfit True

    #             if h.who:

    #                 label h.who:
    #                     style "history_name"
    #                     substitute False

    #                     ## 从 Character 对象中获取叙述角色的文字颜色，如果设置了
    #                     ## 的话。
    #                     if "color" in h.who_args:
    #                         text_color h.who_args["color"]

    #             $ what = renpy.filter_text_tags(h.what, allow=gui.history_allow_tags)
    #             text what:
    #                 substitute False

    #     if not _history_list:
    #         label _("尚无对话历史记录。")


## 此代码决定了允许在历史记录屏幕上显示哪些标签。

define gui.history_allow_tags = { "alt", "noalt", "rt", "rb", "art" }


style history_window is empty

style history_name is gui_label
style history_name_text is gui_label_text
style history_text is gui_text

style history_label is gui_label
style history_label_text is gui_label_text

style history_window:
    xfill True
    ysize gui.history_height

style history_name:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text:
    min_width gui.history_name_width
    textalign gui.history_name_xalign

style history_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    textalign gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label:
    xfill True

style history_label_text:
    xalign 0.5


## 帮助屏幕 ########################################################################
##
## 提供有关键盘和鼠标映射信息的屏幕。它使用其它屏幕（keyboard_help、mouse_help
## 和 gamepad_help）来显示实际的帮助内容。

screen help():

    tag menu

    default device = "keyboard"

    use game_menu(_("帮助"))

    # use game_menu(_("帮助"), scroll="viewport"):

    #     style_prefix "help"

    #     vbox:
    #         spacing 23

    #         hbox:

    #             textbutton _("键盘") action SetScreenVariable("device", "keyboard")
    #             textbutton _("鼠标") action SetScreenVariable("device", "mouse")

    #             if GamepadExists():
    #                 textbutton _("手柄") action SetScreenVariable("device", "gamepad")

    #         if device == "keyboard":
    #             use keyboard_help
    #         elif device == "mouse":
    #             use mouse_help
    #         elif device == "gamepad":
    #             use gamepad_help


screen keyboard_help():

    hbox:
        label _("回车")
        text _("推进对话并激活界面。")

    hbox:
        label _("空格")
        text _("在没有选择的情况下推进对话。")

    hbox:
        label _("方向键")
        text _("导航界面。")

    hbox:
        label _("Esc")
        text _("访问游戏菜单。")

    hbox:
        label _("键盘")
        text _("按住时快进对话。")

    hbox:
        label _("Tab")
        text _("切换对话快进。")

    hbox:
        label _("上一页")
        text _("回退至先前的对话。")

    hbox:
        label _("下一页")
        text _("向前至后来的对话。")

    hbox:
        label "H"
        text _("隐藏用户界面。")

    hbox:
        label "S"
        text _("截图。")

    hbox:
        label "V"
        text _("切换辅助{a=https://doc.renpy.cn/zh-CN/self_voicing.html}机器朗读{/a}。")

    hbox:
        label "Shift+A"
        text _("打开无障碍菜单。")


screen mouse_help():

    hbox:
        label _("左键点击")
        text _("推进对话并激活界面。")

    hbox:
        label _("中键点击")
        text _("隐藏用户界面。")

    hbox:
        label _("右键点击")
        text _("访问游戏菜单。")

    hbox:
        label _("鼠标滚轮上")
        text _("回退至先前的对话。")

    hbox:
        label _("鼠标滚轮下")
        text _("向前至后来的对话。")


screen gamepad_help():

    hbox:
        label _("右扳机键/nA/底键")
        text _("推进对话并激活界面。")

    hbox:
        label _("左扳机键/n左肩键")
        text _("回退至先前的对话。")

    hbox:
        label _("右肩键")
        text _("向前至后来的对话。")

    hbox:
        label _("十字键，摇杆")
        text _("导航界面。")

    hbox:
        label _("开始，向导，B/右键")
        text _("访问游戏菜单。")

    hbox:
        label _("Y/顶键")
        text _("隐藏用户界面。")

    textbutton _("校准") action GamepadCalibrate()


style help_button is gui_button
style help_button_text is gui_button_text
style help_label is gui_label
style help_label_text is gui_label_text
style help_text is gui_text

style help_button:
    properties gui.button_properties("help_button")
    xmargin 12

style help_button_text:
    properties gui.text_properties("help_button")

style help_label:
    xsize 375
    right_padding 30

style help_label_text:
    size gui.text_size
    xalign 1.0
    textalign 1.0



################################################################################
## 其他屏幕
################################################################################


## 确认屏幕 ########################################################################
##
## 当 Ren'Py 需要询问用户有关确定或取消的问题时，会调用确认屏幕。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#confirm

screen confirm(message, yes_action, no_action):

    ## 显示此屏幕时，确保其他屏幕无法输入。
    modal True

    zorder 200

    style_prefix "confirm"

    add '#000000' alpha 0.5

    # add "gui/overlay/confirm.png"
    add '确认框_底图' xycenter(0.5,0.5)

    fixed:

        label _(message):
            style "confirm_prompt"
            align(0.5,0.44)

        hbox:
            align(0.5,0.7)
            spacing 30

            for name,the_action in {_("确定"):yes_action, _("取消"):no_action}.items():

                button:
                    xysize(412,98)
                    
                    if the_hover_button == name:
                        add '确认框_按钮_焦点'
                    else:
                        add '确认框_按钮_默认'

                    text name:
                        if the_hover_button == name:
                            xycenter(0.5,0.58)
                        else:
                            xycenter(0.5,0.52)
                        size 40
                        color "#4C3D3D"
                        outlines [(absolute(3), "#ffffff", absolute(0), absolute(0))]

                    hovered SetScreenVariable('the_hover_button',name)
                    unhovered SetScreenVariable('the_hover_button','')
                    action the_action
            
            # button:
            #     xysize(412,98)
            #     text _("确定")
            #     add '确认框_按钮_默认'
            #     action yes_action

            # hbox:
            #     xalign 0.5
            #     spacing 150

            #     textbutton _("确定") action yes_action
            #     textbutton _("取消") action no_action

    ## 右键点击退出并答复 no（取消）。
    key "game_menu" action no_action


style confirm_frame is gui_frame
style confirm_prompt is gui_prompt
style confirm_prompt_text is gui_prompt_text
style confirm_button is gui_medium_button
style confirm_button_text is gui_medium_button_text

style confirm_frame:
    # background Frame([ "gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    # background Frame('images/UI素材/确认/确认框_底图.png', gui.confirm_frame_borders, tile=gui.frame_tile)
    # padding gui.confirm_frame_borders.padding
    # background 
    xalign .5
    yalign .5

style confirm_prompt_text:
    textalign 0.5
    layout "subtitle"
    color "#000000"

style confirm_button:
    properties gui.button_properties("confirm_button")

style confirm_button_text:
    properties gui.text_properties("confirm_button")


## 快进指示屏幕 ######################################################################
##
## skip_indicator 屏幕用于指示快进正在进行中。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#skip-indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 9
            ypos 0.25
            xpos 0.05

            text _("正在快进"):
                xycenter(0.6,0.52)
                size 24
                color "#4C3D3D"
                outlines [(absolute(3), "#ffffff", absolute(0), absolute(0))]

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## 此变换用于一个接一个地闪烁箭头。
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty
style skip_text is gui_text
style skip_triangle is skip_text

style skip_frame:
    ypos gui.skip_ypos
    # background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    background '对话_通知框'
    padding gui.skip_frame_borders.padding

style skip_text:
    size gui.notify_text_size

style skip_triangle:
    ## 我们必须使用包含“▸”（黑色右旋小三角）字形的字体。
    font "DejaVuSans.ttf"
    color "#4C3D3D"
    outlines [(absolute(3), "#ffffff", absolute(0), absolute(0))]


## 通知屏幕 ########################################################################
##
## 通知屏幕用于向用户显示消息。（例如，当游戏快速保存或进行截屏时。）
##
## https://doc.renpy.cn/zh-CN/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        xysize(258, 68)
        text "[message!tq]":
            xycenter(0.6,0.5)
            size 24
            color "#4C3D3D"
            outlines [(absolute(3), "#ffffff", absolute(0), absolute(0))]

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty
style notify_text is gui_text

style notify_frame:
    ypos gui.notify_ypos

    # background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    background '对话_通知框'
    padding gui.notify_frame_borders.padding

style notify_text:
    properties gui.text_properties("notify")


## NVL 模式屏幕 ####################################################################
##
## 此屏幕用于 NVL 模式的对话和菜单。
##
## https://doc.renpy.cn/zh-CN/screen_special.html#nvl


screen nvl(dialogue, items=None):

    window:
        style "nvl_window"

        has vbox:
            spacing gui.nvl_spacing

        ## 在 vpgrid 或 vbox 中显示对话框。
        if gui.nvl_height:

            vpgrid:
                cols 1
                yinitial 1.0

                use nvl_dialogue(dialogue)

        else:

            use nvl_dialogue(dialogue)

        ## 显示菜单，如果给定的话。如果 config.narrator_menu 设置为 True，则菜单
        ## 可能显示不正确。
        for i in items:

            textbutton i.caption:
                action i.action
                style "nvl_button"

    add SideImage() xalign 0.0 yalign 1.0


screen nvl_dialogue(dialogue):

    for d in dialogue:

        window:
            id d.window_id

            fixed:
                yfit gui.nvl_height is None

                if d.who is not None:

                    text d.who:
                        id d.who_id

                text d.what:
                    id d.what_id


## 此语句控制一次可以显示的 NVL 模式条目的最大数量。
define config.nvl_list_length = gui.nvl_list_length

style nvl_window is default
style nvl_entry is default

style nvl_label is say_label
style nvl_dialogue is say_dialogue

style nvl_button is button
style nvl_button_text is button_text

style nvl_window:
    xfill True
    yfill True

    background "gui/nvl.png"
    padding gui.nvl_borders.padding

style nvl_entry:
    xfill True
    ysize gui.nvl_height

style nvl_label:
    xpos gui.nvl_name_xpos
    xanchor gui.nvl_name_xalign
    ypos gui.nvl_name_ypos
    yanchor 0.0
    xsize gui.nvl_name_width
    min_width gui.nvl_name_width
    textalign gui.nvl_name_xalign

style nvl_dialogue:
    xpos gui.nvl_text_xpos
    xanchor gui.nvl_text_xalign
    ypos gui.nvl_text_ypos
    xsize gui.nvl_text_width
    min_width gui.nvl_text_width
    textalign gui.nvl_text_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_thought:
    xpos gui.nvl_thought_xpos
    xanchor gui.nvl_thought_xalign
    ypos gui.nvl_thought_ypos
    xsize gui.nvl_thought_width
    min_width gui.nvl_thought_width
    textalign gui.nvl_thought_xalign
    layout ("subtitle" if gui.nvl_text_xalign else "tex")

style nvl_button:
    properties gui.button_properties("nvl_button")
    xpos gui.nvl_button_xpos
    xanchor gui.nvl_button_xalign

style nvl_button_text:
    properties gui.text_properties("nvl_button")


## 对话气泡屏幕 ######################################################################
##
## 对话气泡屏幕用于以对话气泡的形式向玩家显示对话。对话气泡屏幕的参数与 say 屏幕
## 相同，必须创建一个 id 为 what 的可视控件，并且可以创建 id 为 namebox、who 和
## window 的可视控件。
##
## https://doc.renpy.cn/zh-CN/bubble.html#bubble-screen

screen bubble(who, what):
    style_prefix "bubble"

    window:
        id "window"

        if who is not None:

            window:
                id "namebox"
                style "bubble_namebox"

                text who:
                    id "who"

        text what:
            id "what"

style bubble_window is empty
style bubble_namebox is empty
style bubble_who is default
style bubble_what is default

style bubble_window:
    xpadding 30
    top_padding 5
    bottom_padding 5

style bubble_namebox:
    xalign 0.5

style bubble_who:
    xalign 0.5
    textalign 0.5
    color "#000"

style bubble_what:
    align (0.5, 0.5)
    text_align 0.5
    layout "subtitle"
    color "#000"

define bubble.frame = Frame("gui/bubble.png", 55, 55, 55, 95)
define bubble.thoughtframe = Frame("gui/thoughtbubble.png", 55, 55, 55, 55)

define bubble.properties = {
    "bottom_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "bottom_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=1),
        "window_bottom_padding" : 27,
    },

    "top_left" : {
        "window_background" : Transform(bubble.frame, xzoom=1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "top_right" : {
        "window_background" : Transform(bubble.frame, xzoom=-1, yzoom=-1),
        "window_top_padding" : 27,
    },

    "thought" : {
        "window_background" : bubble.thoughtframe,
    }
}

define bubble.expand_area = {
    "bottom_left" : (0, 0, 0, 22),
    "bottom_right" : (0, 0, 0, 22),
    "top_left" : (0, 22, 0, 0),
    "top_right" : (0, 22, 0, 0),
    "thought" : (0, 0, 0, 0),
}



################################################################################
## 移动设备界面
################################################################################

style pref_vbox:
    variant "medium"
    xsize 675

## 由于可能没有鼠标，我们将快捷菜单替换为一个使用更少、更大按钮的版本，这样更容
## 易触摸。
screen quick_menu():
    variant "touch"

    zorder 100

    if quick_menu:

        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 1.0

            textbutton _("回退") action Rollback()
            textbutton _("快进") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("自动") action Preference("auto-forward", "toggle")
            textbutton _("菜单") action ShowMenu()


style window:
    variant "small"
    background "gui/phone/textbox.png"

style radio_button:
    variant "small"
    foreground "gui/phone/button/radio_[prefix_]foreground.png"

style check_button:
    variant "small"
    foreground "gui/phone/button/check_[prefix_]foreground.png"

style nvl_window:
    variant "small"
    background "gui/phone/nvl.png"

style main_menu_frame:
    variant "small"
    background "gui/phone/overlay/main_menu.png"

style game_menu_outer_frame:
    variant "small"
    background "gui/phone/overlay/game_menu.png"

style game_menu_navigation_frame:
    variant "small"
    xsize 510

style game_menu_content_frame:
    variant "small"
    top_margin 0

style pref_vbox:
    variant "small"
    xsize 600

style bar:
    variant "small"
    ysize gui.bar_size
    left_bar Frame("gui/phone/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
    right_bar Frame("gui/phone/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    variant "small"
    xsize gui.bar_size
    top_bar Frame("gui/phone/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/phone/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style scrollbar:
    variant "small"
    ysize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/horizontal_[prefix_]bar.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/horizontal_[prefix_]thumb.png", gui.scrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    variant "small"
    xsize gui.scrollbar_size
    base_bar Frame("gui/phone/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
    thumb Frame("gui/phone/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style slider:
    variant "small"
    ysize gui.slider_size
    base_bar Frame("gui/phone/slider/horizontal_[prefix_]bar.png", gui.slider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/horizontal_[prefix_]thumb.png"

style vslider:
    variant "small"
    xsize gui.slider_size
    base_bar Frame("gui/phone/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/phone/slider/vertical_[prefix_]thumb.png"

style slider_vbox:
    variant "small"
    xsize None

style slider_slider:
    variant "small"
    xsize 900
