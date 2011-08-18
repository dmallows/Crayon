import sys
import gtk
import gobject

class GraphViewer(object):

    def on_window_delete(self, widget, data=None):
        print "quit!"
        gtk.main_quit()
        return False

    def on_canvas_expose_event(self, da, event, data=None):
        x, y, w, h = da.allocation
        cr = da.window.cairo_create()
        cr.set_source_rgb(0,0,0)
        cr.rectangle(0, 0, w, h)
        cr.fill()
        return True

    def on_change_row(self, treeview):
        model, iter = treeview.get_selection().get_selected()
        val, = model.get(iter, 0)
        print val

    def __init__(self):
    
        builder = gtk.Builder()
        builder.add_from_file("test.glade") 
        
        self.treeview = builder.get_object("treeview")
        table = builder.get_object("paramtable")
        
        model = gtk.TreeStore(str)
        iter = model.append(None, ('foo',))
        iter = model.append(iter, ('foo.1',))
        iter = model.append(iter, ('foo.1.1',))
        iter = model.append(None, ('bar',))
        iter = model.append(None, ('baz',))

        self.treeview.set_model(model)

        cell = gtk.CellRendererText()

        column = gtk.TreeViewColumn("Object", cell, text=0)
        
        table.resize(5, 2)
        x = gtk.EXPAND | gtk.FILL
        for i in xrange(5):
            label = gtk.Label('%04d' % i)
            entry = gtk.Entry()
            table.attach(label, 0, 1, i, i+1, x, 0)
            table.attach(entry, 1, 2, i, i+1, x, 0)
        
        self.treeview.append_column(column)
        self.treeview.connect('cursor-changed', self.on_change_row)

        builder.connect_signals(self)       
        self.window = builder.get_object("window")
        self.window.show_all()

if __name__ == "__main__":
    editor = GraphViewer()
    gtk.main()
