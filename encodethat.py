import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup

#fx to simplify ui creation
class uiElementHandler():
    def makeLbl(self,title, phint, fsize=None):
        if(fsize==None):
            fsize = 30  #Set to 30 if not declared
        shint = (0.5,0.1)
        h_align = 'center'
        v_align = 'middle'
        return Label(text=str(title), font_size=fsize, size_hint=shint, pos_hint=phint, halign = h_align, valign=v_align)

    def makeBtn(self,title, phint, callback, enableBtn=None, shint=None, fsize=None):
        if(fsize==None):
            fsize = 40                 #Default font size
        if(shint==None):
            shint = (0.3,0.2)        #Size 25% of screen size, width height
        if(enableBtn==None):
            enableBtn = False
        return Button(text=title,font_size=fsize,size_hint=shint, pos_hint = phint, on_press=callback, disabled=not enableBtn)

#Home screen
class MainScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        uiHdl = uiElementHandler()
        self.eList = []
        self.layout = FloatLayout()
        self.lblTitle = uiHdl.makeLbl("[color=#baed91]Encode[/color] that!", {"x":0.25,"top":0.9}, fsize=70)
        self.lblTitle.markup = True
        self.eList.append(self.lblTitle)
        self.btnStart = uiHdl.makeBtn("Start", {"x":0.25,"top":0.6}, self.startGameScreen, enableBtn=True, shint=(0.5,0.15))
        self.eList.append(self.btnStart)
        self.btnSettings = uiHdl.makeBtn("Settings", {"x":0.25,"top":0.4}, self.startSettingsScreen,enableBtn=True, shint=(0.5,0.15))
        self.eList.append(self.btnSettings)
        self.btnQuit = uiHdl.makeBtn("Quit", {"x":0.25,"top":0.2}, self.exitGame,enableBtn=True, shint=(0.5,0.15))
        self.eList.append(self.btnQuit)

        for k in self.eList:
            self.layout.add_widget(k)

        self.add_widget(self.layout)


    def startGameScreen(self, value):
        self.manager.transition.direction = 'left'
        self.manager.current = "game_screen"

    def startSettingsScreen(self, value):
        self.manager.transition.direction = 'up'
        self.manager.current = "settings_screen"

    def exitGame(self, value):
        App.get_running_app().stop()
        Window.close()

class GameScreen(Screen):
    elemList = []


    #Timer
    cTimerActive = False                   #Countdown timer state
    pauseTimer = False
    timeLeft = 0                           #Time left before timer expiry

    #Timer activity identifier ID constants
    READY_COUNTDOWN = 156                #ID for countdown before game start
    GAME_COUNTDOWN = 201                #ID for main game countdown

    #Game var
    DURATION_GAME = 60                 #Game duration
    gameActive = False

    #Button timing/setting
    isBtnTimerActive = False
    timeAfterPress = 0
    btnTimerUpdateInterval = 100 #How often the timer updates
    timeSpacing = 300      #Wait n milliseconds before resting text

    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = FloatLayout()
        #Add UI elements
        self.elemList = self.initUIElem(self.elemList)
        #Add widgets
        for el in self.elemList:
            self.layout.add_widget(el)
        self.add_widget(self.layout)

    def initUIElem(self,eList):     #Layout, element_list
        self.uiHandle = uiElementHandler()
        #Score
        self.lblScore = self.uiHandle.makeLbl("Score: 000000", {"x":0, "top":1})
        eList.append(self.lblScore)

        #Score
        self.lblTimer = self.uiHandle.makeLbl("Timer: 000", {"x":0.5, "top":1})
        eList.append(self.lblTimer)

        #Word to code
        self.lblCodeword = self.uiHandle.makeLbl('{} [color=#E5D209]{}[/color] {}'.format("Press","Go","to begin..."), {"x":0.25, "y":0.5}, fsize=70)
        self.lblCodeword.markup = True
        eList.append(self.lblCodeword)

        #User entry
        self.lblUser = self.uiHandle.makeLbl("Idle", {"x":0.25, "y":0.25}, )
        eList.append(self.lblUser)

        #Dot
        self.btnDot = self.uiHandle.makeBtn(
            '•',
            {"x":0, "right":0.5},  #Right ends at 0.5 of screen
            self.dotPress
            )
        eList.append(self.btnDot)

        #Dash
        self.btnDash = self.uiHandle.makeBtn(
            '—',
            {"x":0.5, "left":0},  #Right ends at 0.5 of screen
            self.dashPress
            )
        eList.append(self.btnDash)

        #Start btn ontop of usercode
        self.btnGo = self.uiHandle.makeBtn(
            'Go',
            {"x":0.25,"y":0.25},
            self.goPress,
            enableBtn = True,
            shint=(0.5,0.15)
        )
        eList.append(self.btnGo)

        self.btnPause = self.uiHandle.makeBtn(
            'Menu',
            {"x":0.4,"top":1},
            self.pausePress,
            enableBtn = True,
            shint=(0.2,0.1),
            fsize=30
        )
        eList.append(self.btnPause)

        return eList

    def dotPress(self, instance):
        print('\a')
        self.setUserText("•",self.elemList[3])
        self.trackBtnTime()

    def dashPress(self, instance):
        self.setUserText("—",self.elemList[3])
        self.trackBtnTime()

    def setUserText(self, text, lbl):
        lbl.text += text
        if(len(lbl.text)>5):
            self.resetTypedText(lbl)   #Reset text after more than 5 char

    #Clear text
    def resetTypedText(self, lbl):
        lbl.text = ""



    def resetGame(self):
        if(self.cTimerActive):
            Clock.unschedule(self.onUpdateTime) #Stop timer
            self.cTimerActive = False
        self.elemList[1].text = "Timer: 000"
        self.elemList[2].text = '{} [color=#E5D209]{}[/color] {}'.format("Press","Go","to begin...")
        #Enable main btns
        self.elemList[4].disabled = True
        self.elemList[5].disabled = True
        #Hide go btn
        self.elemList[6].disabled = False
        self.elemList[6].opacity = 100


    #       BUTTON CALLBACK(S)

    def goPress(self, instance):
        #Change game title, countdown from 3 then start
        self.elemList[2].text = "Ready?"
        self.countdownTime(3,self.READY_COUNTDOWN)
        #Enable main btns
        self.elemList[4].disabled = False
        self.elemList[5].disabled = False
        #Hide go btn
        self.elemList[6].disabled = True
        self.elemList[6].opacity = 0

    def pausePress(self, instance):
        if(self.cTimerActive):
            self.pauseTimer = True
        emList = []
        popupLayout = FloatLayout()
        btnResume = self.uiHandle.makeBtn(
        'Resume',
        {"x":0.25, "top":0.9},  #Right ends at 0.5 of screen
        self.resumePress,
        shint=(0.5,0.4),
        enableBtn=True
        )
        emList.append(btnResume)

        btnQuit = self.uiHandle.makeBtn(
        'Quit',
        {"x":0.25, "top":0.45},  #Right ends at 0.5 of screen
        self.quitPress,
        shint=(0.5,0.4),
        enableBtn=True
        )
        emList.append(btnQuit)

        for el in emList:
            popupLayout.add_widget(el)

        self.popupMenu = Popup(title='Game Paused',
            content=popupLayout,
            size_hint=(None, None), size=(400, 250),
            auto_dismiss=False)

        self.popupMenu.open()

    def resumePress(self,instance):
        if(self.cTimerActive):
            self.pauseTimer = False
        self.popupMenu.dismiss()

    def quitPress(self,instance):
        self.popupMenu.dismiss()
        self.manager.transition.direction = 'right'
        self.manager.current = "main_screen"
        self.resetGame()

    #       TIMER(S)

    #Duration to countdown, seconds
    #Label to update
    def countdownTime(self,tm, call_id):
        self.timeLeft = tm
        self.countdown_act_id = call_id         #Register current
        self.cTimerActive = True
        self.pauseTimer = False
        Clock.schedule_interval(self.onUpdateTime, 1) #Refresh every 1s

    def onUpdateTime(self, dt): #Refresh duration -> dt
        #self.elemList[2].text = 'Time: {:03d}'.format(self.t)
        if(self.cTimerActive):
            if(self.timeLeft!=0):
                if(self.countdown_act_id == self.READY_COUNTDOWN):
                    self.elemList[2].text = str(self.timeLeft)
                elif(self.countdown_act_id == self.GAME_COUNTDOWN):
                    self.elemList[1].text = "Timer: "+str(self.timeLeft)

                if(not self.pauseTimer):
                    self.timeLeft -= 1
            else:
                Clock.unschedule(self.onUpdateTime) #Stop timer
                if(self.countdown_act_id == self.READY_COUNTDOWN):
                    self.elemList[2].text = "Begin!"
                    self.resetTypedText(self.elemList[3])                           #Set player text as empty
                    self.countdownTime(self.DURATION_GAME,self.GAME_COUNTDOWN)    #Start game timer
                elif(self.countdown_act_id == self.READY_COUNTDOWN):
                    self.timeLeft -= 1
                    self.elemList[1].text = "Timer: "+str(self.timeLeft)
                    self.elemList[2].text = "Game Over"


    #Keep track of button press
    def trackBtnTime(self):
        #Reset timing
        self.timeAfterPress = self.timeSpacing
        if(not self.isBtnTimerActive):
            self.isBtnTimerActive = True         #Start btn timer tracking
            Clock.schedule_interval(self.btnTimeTrackUpdate, self.btnTimerUpdateInterval/1000) #Refresh every 200ms

    def btnTimeTrackUpdate(self, dt):
        if(self.isBtnTimerActive):
            if(self.timeAfterPress!=0):
                self.timeAfterPress -= 100
            else:
                self.elemList[3].text = ""
                self.isBtnTimerActive = False
                Clock.unschedule(self.btnTimeTrackUpdate)


class encodeThat(App):
    #Set screen size
    SWIDTH = 800
    SHEIGHT = 500

    def build(self):
        Window.size = (self.SWIDTH, self.SHEIGHT)    #Set window size
        self.title = "Encode that!"
        sm = ScreenManager()
        ms = MainScreen(name="main_screen")
        gs = GameScreen(name="game_screen")
        #st = SettingsScreen(name='settings_screen')
        sm.add_widget(ms)
        sm.add_widget(gs)

        #sm.add_widget(st)
        sm.current = "main_screen"
        return sm


if __name__ == "__main__":
    encodeThat().run()
