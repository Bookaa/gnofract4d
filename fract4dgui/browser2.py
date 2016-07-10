#!/usr/bin/env python

# a browser to examine fractal functions
import string

import gobject
import gtk

from fract4d import browser_model, fc

import dialog, utils, gtkfractal

def show(parent, f, type=browser_model.FRACTAL):
    _browser = dialog.reveal(BrowserDialog,True, parent, None, f)
    _browser.set_type(type)
    GG_Instance.update(f.forms[0].funcFile, f.forms[0].funcName)
    _browser.populate_file_list()

# from browser import GG_Instance
class GG_Instance:
    _instance = browser_model.T(fc.instance)

    @classmethod
    def update(cls, file=None, formula=None):
        cls._instance.update(file,formula)

    @classmethod
    def set_type(cls, type):
        cls._instance.set_type(type)

    @classmethod
    def guess_type(cls, file):
        return cls._instance.guess_type(file)


class BrowserDialog(dialog.T):
    RESPONSE_EDIT = 1
    RESPONSE_REFRESH = 2
    RESPONSE_COMPILE = 3
    def __init__(self,main_window,f):
        dialog.T.__init__(
            self,
            _("Formula Browser with Preview"),
            main_window,
            gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_REFRESH, BrowserDialog.RESPONSE_REFRESH,
             gtk.STOCK_APPLY, gtk.RESPONSE_APPLY,
             gtk.STOCK_OK, gtk.RESPONSE_OK,
             gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))

        self.set_default_response(gtk.RESPONSE_OK)

        self.model = GG_Instance._instance
        self.model.type_changed += self.on_type_changed
        self.model.file_changed += self.on_file_changed
        self.model.formula_changed += self.on_formula_changed
        
        self.formula_list = gtk.ListStore(gobject.TYPE_STRING)

        self.file_list = gtk.ListStore(
            gobject.TYPE_STRING, #formname
            gobject.TYPE_STRING,
            gobject.TYPE_INT)

        self.f = f
        self.compiler = f.compiler
        self.last_preview = None

        #self.ir = None
        self.main_window = main_window
        self.set_size_request(1340,840)

        self.create_panes()
        self.on_file_changed()
        
    def onResponse(self,widget,id):
        if id == gtk.RESPONSE_CLOSE or \
               id == gtk.RESPONSE_NONE or \
               id == gtk.RESPONSE_DELETE_EVENT:
            self.hide()
        elif id == gtk.RESPONSE_APPLY:
            self.onApply()
        elif id == gtk.RESPONSE_OK:
            self.onApply()
            self.hide()
        elif id == BrowserDialog.RESPONSE_REFRESH:
            self.onRefresh()
        else:
            print "unexpected response %d" % id

    def onRefresh(self):
        self.f.refresh()
        self.set_file(self.model.current.fname) # update text window

    def onApply(self):
        self.model.apply(self.f)
        
    def set_type_cb(self,optmenu):
        self.set_type(utils.get_selected(optmenu))

    def on_type_changed(self):
        utils.set_selected(self.funcTypeMenu, self.model.current_type)
        self.populate_file_list()
        
    def set_type(self,type):
        self.model.set_type(type)
        
    def create_file_list(self):
        sw = gtk.ScrolledWindow()

        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.filetreeview = gtk.TreeView (self.file_list)
        self.filetreeview.set_tooltip_text(_("A list of files containing fractal formulas"))
        
        sw.add(self.filetreeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn ('_File', renderer, text=0)
        
        self.filetreeview.append_column (column)

        selection = self.filetreeview.get_selection()
        selection.connect('changed',self.file_selection_changed)
        return sw

    def populate_file_list(self):
        # find all appropriate files and add to file list
        formula = self.model.current.formula
        self.file_list.clear()

        files = self.model.current.files
        
        current_iter = None
        index,i = 0,0
        for fname in files:
            iter = self.file_list.append ()
            if fname == self.model.current.fname:
                current_iter = iter
                index = i
            self.file_list.set (iter, 0, fname)
            i += 1
            
        # re-select current file, if any
        if current_iter:
            self.filetreeview.scroll_to_cell(index)
            sel = self.filetreeview.get_selection()
            if sel:
                sel.unselect_all()
                sel.select_iter(current_iter)
                self.populate_formula_list(self.model.current.fname, formula)
        else:
            self.formula_list.clear()
            self.formula_selection_changed(None)
        
    def populate_formula_list(self, fname, formula):
        self.formula_list.clear()

        form_names = self.model.current.formulas

        # formula = self.model.current.formula
        for i, formula_name in enumerate(form_names):
            iter = self.formula_list.append()
            self.formula_list.set(iter,0,formula_name)

            if formula_name == formula:
                self.treeview.get_selection().select_iter(iter)
                self.treeview.scroll_to_cell(i)
                self.set_formula(formula_name)


        if fname == self.lastfname:
            return

        self.lastfname = fname
        self.last_preview = None

        for i, formula_name in enumerate(form_names):
            if formula_name == self.model.current.formula:
                break
        else:
            i = 0

        firstpos = (i / 16) * 16

        self.DoDraw16(firstpos)

    def create_formula_list(self):
        sw = gtk.ScrolledWindow ()
        sw.set_shadow_type (gtk.SHADOW_ETCHED_IN)
        sw.set_policy (gtk.POLICY_NEVER,
                       gtk.POLICY_AUTOMATIC)

        self.treeview = gtk.TreeView (self.formula_list)

        self.treeview.set_tooltip_text(_("A list of formulas in the selected file"))

        sw.add(self.treeview)

        renderer = gtk.CellRendererText ()
        column = gtk.TreeViewColumn (_('F_ormula'), renderer, text=0)
        self.treeview.append_column (column)

        selection = self.treeview.get_selection()
        selection.connect('changed',self.formula_selection_changed)
        return sw

    def create_panes(self):
        # option menu for choosing Inner/Outer/Fractal
        self.funcTypeMenu = utils.create_option_menu(
            [_("Fractal Function"),
             _("Outer Coloring Function"),
             _("Inner Coloring Function"),
             _("Transform Function"),
             _("Gradient")])

        utils.set_selected(self.funcTypeMenu,self.model.current_type)
        
        self.funcTypeMenu.set_tooltip_text(_("Which formula of the current fractal to change"))

        self.funcTypeMenu.connect('changed',self.set_type_cb)

        # label for the menu
        hbox = gtk.HBox()
        label = gtk.Label(_("Function _Type to Modify : "))
        label.set_use_underline(True)
        label.set_mnemonic_widget(self.funcTypeMenu)
        
        hbox.pack_start(label, False, False)
                
        hbox.pack_start(self.funcTypeMenu,True, True)
        self.vbox.pack_start(hbox,False, False)
        
        # 3 panes: files, formulas, formula contents
        panes1 = gtk.HPaned()
        self.vbox.pack_start(panes1, True, True)
        panes1.set_border_width(5)

        file_list = self.create_file_list()
        formula_list = self.create_formula_list()
        
        panes2 = gtk.HPaned()
        # left-hand pane displays file list
        panes2.add1(file_list)
        # middle is formula list for that file
        panes2.add2(formula_list)        
        panes1.add1(panes2)

        # preview
        self.previews = []
        self.lastfname = ''
        self.firstpos = 0

        self.ftable = gtk.Table(4,4,True)

        for i in range(16):
            preview = gtkfractal.Preview(self.compiler)
            self.previews.append((preview,''))
            self.ftable.attach(preview.widget, i%4,(i%4)+1,i/4,(i/4)+1) #, 0, 0, 1, 1)

        sw = gtk.ScrolledWindow()
        sw.add_with_viewport(self.ftable)

        panes1.add2(sw)

    def file_selection_changed(self,selection):
        self.model.current.formula = None
        (model,iter) = selection.get_selected()
        if iter == None:
            return
        
        fname = model.get_value(iter,0)
        self.set_file(fname)

    def set_file(self,fname):
        self.model.set_file(fname)

    def on_file_changed(self):
        text = self.model.get_contents()
        
        self.populate_formula_list(self.model.current.fname, self.model.current.formula)
        self.set_apply_sensitivity()
        
    def clear_selection(self):
        self.set_formula(None)
        
    def formula_selection_changed(self,selection):
        if not selection:
            self.clear_selection()
            return
        
        (model,iter) = selection.get_selected()
        if iter == None:
            self.clear_selection()
            return
        
        form_name = model.get_value(iter,0)
        self.set_formula(form_name)
        
    def set_formula(self,form_name):
        self.model.set_formula(form_name)

    def on_formula_changed(self):
        form_name = self.model.current.formula
        file = self.model.current.fname

        if not file:
            return
        
        formula = self.compiler.get_parsetree(file,form_name)

        if not formula:
            return
        
        self.set_apply_sensitivity()

    def set_apply_sensitivity(self):
        can_apply = self.model.current.can_apply
        self.set_response_sensitive(gtk.RESPONSE_APPLY,can_apply)
        self.set_response_sensitive(gtk.RESPONSE_OK,can_apply)


        if can_apply:
            fname = self.model.current.fname
            form_names = self.model.current.formulas
            for i, formula_name in enumerate(form_names):
                if formula_name == self.model.current.formula:
                    break
            else:
                print 'why not find current'
                i = 0
            firstpos = (i / 16) * 16
            i = i % 16
            if firstpos != self.firstpos:
                print 'firstpos change', self.firstpos, firstpos
                self.DoDraw16(firstpos)
                return


            if self.last_preview:
                preview, formula_name1 = self.last_preview

                f2 = self.f.copy_f()
                f2.set_formula(fname, formula_name1, self.model.current_type)
                preview.set_fractal(f2)
                preview.draw_image(False)
                print 'last', fname, formula_name1
            preview, formula_name1 = self.previews[i]
            if formula_name != formula_name1:
                print 'why not coe:', formula_name, formula_name1

            f2 = self.f.copy_f()
            f2.set_formula(fname, formula_name1, self.model.current_type)
            f2.set_cmap('maps/basic.map')
            preview.set_fractal(f2)

            self.model.apply(preview)
            preview.draw_image(False, False)

            self.last_preview = preview, formula_name1
            print 'current', fname, formula_name1, self.model.current_type

    def DoDraw16(self, firstpos):
        self.firstpos = firstpos

        form_names = self.model.current.formulas

        fname = self.model.current.fname
        ii=0
        for i, formula_name in enumerate(form_names):
            if i < firstpos:
                continue
            ii = i - firstpos
            if ii >= 16:
                continue
            if True:
                preview, _ = self.previews[ii]
                try:
                    f2 = self.f.copy_f()
                    f2.set_formula(fname, formula_name, self.model.current_type)
                    if formula_name == self.model.current.formula:
                        f2.set_cmap('maps/basic.map')
                        self.last_preview = preview, formula_name
                    preview.set_fractal(f2)
                except:
                    print 'error 3'
                    pass
                preview.widget.show_all()
                preview.draw_image(False)
                self.previews[ii] = (preview, formula_name)
        ii += 1
        while ii < 16:
            preview, _ = self.previews[ii]
            ii += 1
            preview.widget.hide_all()


