#!/usr/bin/python
#coding:utf-8

import sys, time, gettext, getopt
import ORBit, CORBA
import gtk

prgName = "rtbfms"
gettext.install(prgName)

def usage():
  print _("RTBFMS DEMO, Version 1.1, Last modified 2004-12-04")
  print
  print _("Usage: %s [options]") % sys.argv[0]
  print _("-c, --client=sensor|center|shooter    As client")
  print _("-h, --help                            This information")
  print _("-s, --server                          As server")

def server():
  print "Server is running..."
  idlContent = """
// rtbfms.idl
module RTBFMS {
        struct Fighter {
                string id;
                string model;
                short field;
                boolean friend;
                boolean alive;
        };
        struct Command {
                string id;
                string time;
                string content;
        };
        interface Grid {
                typedef sequence<Fighter> FighterList;
                typedef sequence<Command> CommandList;
                attribute FighterList fighters;
                attribute CommandList commands;
                boolean pushFighter(in string FighterID, in Fighter FighterData);
                void pullFighter(in string FighterID, inout Fighter FighterData);
                boolean pushCommand(in string FighterID, in Command CommandData);
                void pullCommand(in string FighterID, inout Command CommandData);
                void quitCommand();
        };
};
"""
  idlFile = file(prgName+".idl","w")
  idlFile.write(idlContent)
  idlFile.close()

  ORBit.load_file(prgName+".idl")
  import RTBFMS__POA
  class Servant(RTBFMS__POA.Grid):
    def __init__(self):
      self.fighters = []
      self.commands = []
    def pushFighter(self,FighterID,FighterData):
      self.fighters.append(FighterData)
      for f in self.fighters:
        print f.id, f.model, len(f.id)
    def pullFighter(self,FighterID,FighterData):
      for fighter in self.fighters:
        if fighter.id == FighterID:
          FighterData = fighter
      return FighterData
    def pushCommand(self,FighterID,CommandData):
      self.commands.append(CommandData)
      for c in self.commands:
        print c.id, c.time, c.content
    def pullCommand(self,FighterID,CommandData):
      for command in self.commands:
        if command.id == FighterID:
          CommandData = command
      return CommandData
    def quitCommand(self):
      orb.shutdown(0)
  orb = CORBA.ORB_init(sys.argv)
  servant = Servant()
  objref = servant._this()
  iorFile = file(prgName+".ior", "w")
  iorFile.write(orb.object_to_string(objref))
  iorFile.close()
  poa = orb.resolve_initial_references("RootPOA")
  poa._get_the_POAManager().activate()
  orb.run()

class Application:
  def __init__(self):
    self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    self.window.set_title(_("即時戰場管理系統雛型"))
    self.window.set_border_width(5)
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.destroy)
             
    self.mainBox = gtk.VBox(False, 3)
    self.window.add(self.mainBox)
    self.topBox = gtk.HBox(False, 3)
    self.mainBox.pack_start(self.topBox, expand=False)
    self.middleFrame = gtk.Frame("戰場示意圖")
    self.middleFrame.set_label_align(0.5,0)
    self.middleFrame.set_shadow_type(gtk.SHADOW_IN)
    self.mainBox.pack_start(self.middleFrame)
    self.bottomBox = gtk.HBox(False, 3)
    self.mainBox.pack_start(self.bottomBox, expand=False)
      
    self.idLabel = gtk.Label(_("ID:"))
    self.topBox.add(self.idLabel)
    self.idEntry = gtk.Entry()
    self.topBox.add(self.idEntry)
    self.passwordLabel = gtk.Label(_("Password:"))
    self.topBox.add(self.passwordLabel)
    self.passwordEntry = gtk.Entry()
    self.topBox.add(self.passwordEntry)
    self.passwordEntry.set_visibility(False)      
    self.connectButton = gtk.Button(stock=gtk.STOCK_ADD)
    self.topBox.add(self.connectButton)
    self.connectButton.connect("clicked", self.connectCall, None)
        
    self.battleArea = gtk.DrawingArea()
    self.battleArea.set_size_request(600,400)
    self.battleArea.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("gray"))
    self.pangolayout = self.battleArea.create_pango_layout("")
    self.middleFrame.add(self.battleArea)
        
    self.aboutButton = gtk.Button(stock=gtk.STOCK_DIALOG_INFO)
    self.bottomBox.pack_start(self.aboutButton,expand=False)
    self.aboutButton.connect("clicked", self.aboutCall, None)
    self.quitButton = gtk.Button(stock=gtk.STOCK_QUIT)
    self.bottomBox.pack_end(self.quitButton,expand=False)
    self.quitButton.connect_object("clicked", gtk.Widget.destroy, self.window)
    
    self.window.show_all()
    self.actionButton = gtk.Button(stock=gtk.STOCK_EXECUTE)
    self.bottomBox.pack_start(self.actionButton,expand=False)
    self.actionButton.connect("clicked", self.actionCall, True)
    
  def connectCall(self, widget, data=None):
    myself.id = self.idEntry.get_text()
    if myself.id == "00":
      myself.model = "中心"
      self.actionButton.show()
    elif myself.id == "01":
      myself.model = "雷達"
    elif myself.id == "02":
      myself.model = "士兵"
    elif myself.id == "03":
      myself.model = "坦克"
    else:
      myself.model = "不明物"
    myself.field = 0
    myself.friend = True
    myself.alive = True
##    servant.pushFighter(myself.id, myself)
        
    self.style = self.battleArea.get_style()
    self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
    self.gcb = self.style.bg_gc[gtk.STATE_NORMAL]
    self.timer = gtk.timeout_add(3000, self.actionCall, self)
        
  def actionCall(self, widget, data=None):
    fighter = RTBFMS.Fighter()
    command = RTBFMS.Command()
    if myself.id == "00" and data:
      command.time = time.ctime()
      command.content = ""
      dialog = gtk.Dialog("指定代號下達命令", self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
      idEntry = gtk.Entry()
      dialog.vbox.add(idEntry)
      contentEntry = gtk.Entry()
      dialog.vbox.add(contentEntry)
      dialog.show_all()
      dialog.run()
      command.id = idEntry.get_text()[0:2]
      command.content = contentEntry.get_text()
      dialog.destroy()
      if command.id == "02" or command.id == "03":
        servant.pushCommand(myself.id, command)
    elif myself.id == "01":
      mySerial = []
      mySerial.append(serial.Serial(0,timeout=1))
      mySerial.append(serial.Serial(1,timeout=1))
      for s in mySerial:
        i = ""
        i = s.readline()
        if i:
          fighter.field = s.port + 1
          fighter.alive = True
          fighter.friend = (i[0] == "0")
          if i[1] == "0":
            fighter.model = "中心"
          elif i[1] == "1":
            fighter.model = "雷達"
          elif i[1] == "2":
            fighter.model = "士兵"
          elif i[1] == "3":
            fighter.model = "坦克"
          else:
            fighter.model = "不明物"
          fighter.id = i[0:2]
          print fighter.id, fighter.field
          servant.pushFighter(myself.id, fighter)
        s.close()
    elif myself.id == "02" or myself.id == "03":
      command.id = ""
      command.time = time.ctime()
      command.content = ""
      c = servant.pullCommand(myself.id, command)
      if c.content:
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
        dialog.set_markup(c.time+"\n<big>"+c.content+"</big>")
        dialog.run()
        dialog.destroy()
        c.content = ""
        servant.pushCommand(myself.id, c)
                
    self.battleArea.window.draw_rectangle(self.gcb, True, 0, 0, 299, 399)
    self.battleArea.window.draw_rectangle(self.gcb, True, 301, 0, 299, 399)
    for id in ["02","03","12","13"]:
      fighter = myself
      fighter.field = 0
      f = servant.pullFighter(id, fighter)
      print f.field, f.id, f.model
      if f.field != 0:
        self.draw_pixmap(f)
    self.pangolayout.set_text("A")
    self.battleArea.window.draw_layout(self.gc, 150, 0, self.pangolayout)
    self.pangolayout.set_text("B")
    self.battleArea.window.draw_layout(self.gc, 450, 0, self.pangolayout)
    self.battleArea.window.draw_line(self.gc, 300, 0, 300, 400)
    return True
    
  def draw_pixmap(self, fighter):
    pixmap, mask = gtk.gdk.pixmap_create_from_xpm(self.battleArea.window, self.style.bg[gtk.STATE_NORMAL], fighter.id+".xpm")
    x = (fighter.field-1)*300+int(fighter.id[0])*120+50
    y = (int(fighter.id[1])-1)*120
    self.battleArea.window.draw_drawable(self.gc, pixmap, 0, 0, x+15, y+25, -1, -1)
    if fighter.friend:
      text = fighter.model+"(我)"+fighter.id
    else:
      text = fighter.model+"(敵)"+fighter.id
    self.pangolayout.set_text(text)
    self.battleArea.window.draw_layout(self.gc, x+5, y+10, self.pangolayout)

  def aboutCall(self, widget, data=None):
    dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, gtk.BUTTONS_OK)
    dialog.set_markup("<big>RTBFMS v1.1</big>\n\nReal-Time Battle Field Management System\n\n<small>Copyright © 2004</small>")
    dialog.run()
    dialog.destroy()

  def destroy(self, widget, data=None):
    if myself.id == "00":
      try:
        servant.quitCommand()
      except:
        print "Server is Down!"
    gtk.timeout_remove(self.timer)
    gtk.main_quit()
    
  def delete_event(self, widget, event, data=None):
    return False

  def main(self):
    gtk.main()

if __name__ == "__main__":
  try:
    opts, pars = getopt.getopt(sys.argv[1:], "hsc:", ["help","server","client="])
  except getopt.GetoptError:
    print _("option not recognized, use -h for help")
    sys.exit(2)
  if not opts:
    usage()
  else:
    sys.argv[1] = "-ORBIIOPIPv4=1"
  for opt, arg in opts:
    if opt in ("-h", "--help"):
      usage()
      sys.exit()
    elif opt in ("-s", "--server"):
      server()
      sys.exit()
    elif opt in ("-c", "--client"):
      ORBit.load_file(prgName+".idl")
      import RTBFMS
      ior = file(prgName+".ior").read()
      orb = CORBA.ORB_init(sys.argv)
      try:
        ior = file(prgName+".ior").read()
        servant = orb.string_to_object(ior)._narrow(RTBFMS.Grid)
      except:
        print "No IOR File"
      myself = RTBFMS.Fighter()
      if arg == "sensor":
        import serial
      application = Application()
      application.main()
      sys.exit()
