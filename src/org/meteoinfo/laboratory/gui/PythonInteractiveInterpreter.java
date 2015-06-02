/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import java.awt.Color;
import org.meteoinfo.console.JavaCharStream;
import org.meteoinfo.console.JConsole;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintStream;
import java.io.Reader;
import javax.swing.event.EventListenerList;
import org.meteoinfo.laboratory.event.ConsoleExecEvent;
import org.meteoinfo.laboratory.event.IConsoleExecListener;
import org.python.core.PyObject;
import org.python.util.InteractiveConsole;

/**
 *
 * @author yaqiang
 */
public class PythonInteractiveInterpreter extends InteractiveConsole implements Runnable {

    transient Reader in;
    transient PrintStream out;
    transient PrintStream err;
    JConsole console;
    private final EventListenerList listeners = new EventListenerList();

    public PythonInteractiveInterpreter(JConsole console) {
        super();

        this.cflags.source_is_utf8 = true;
        this.console = console;
        in = console.getIn();
        out = console.getOut();
        err = console.getErr();
        setOut(out);
        setErr(err);
    }

    @Override
    public void run() {
        boolean eof = false;
        JavaCharStream stream = new JavaCharStream(in, 1, 1);

//        exec("_ps1 = sys.ps1");
//        PyObject ps1Obj = get("_ps1");
//        String ps1 = ps1Obj.toString();
        String ps1 = ">>> ";

//        exec("_ps2 = sys.ps2");
//        PyObject ps2Obj = get("_ps2");
//        String ps2 = ps2Obj.toString();
        String ps2 = "... ";
        //out.print(getDefaultBanner() + "\n");
        this.console.print(getDefaultBanner() + "\n", Color.red);
        //out.print(ps1);
        this.console.print(ps1, Color.red);        
        String line;
        while (!eof) {
            // try to sync up the console
            System.out.flush();
            System.err.flush();
            Thread.yield();  // this helps a little

            try {
                boolean eol = false;
                line = "";

                while (!eol) {
                    char aChar = stream.readChar();
                    eol = (aChar == '\n');
                    if (!eol) {
                        line = line + aChar;
                    }
                }
                line = line.trim();

                //hitting Enter at prompt returns a semicolon
                //get rid of it since it returns an error when executed
                if (line.equals(";")) {
                    line = "";
                }

                boolean retVal = push(line);

                if (retVal) {
                    out.print(ps2);                    
                } else {
                    //out.print(ps1);
                    //this.console.print(ps1, Color.red);
                    this.fireConsoleExecEvent();
                }
            } catch (IOException ex) {
            }
        }
    }
    
    @Override
    public void execfile(InputStream s){
        this.cflags.source_is_utf8 = false;
        super.execfile(s);
        this.cflags.source_is_utf8 = true;
        this.fireConsoleExecEvent();
    }

    public void addConsoleExecListener(IConsoleExecListener listener) {
        this.listeners.add(IConsoleExecListener.class, listener);
    }

    public void removeConsoleExecListener(IConsoleExecListener listener) {
        this.listeners.remove(IConsoleExecListener.class, listener);
    }

    public void fireConsoleExecEvent() {
        fireConsoleExecEvent(new ConsoleExecEvent(this));
        this.console.print(">>> ", Color.red);
        //this.console.setStyle(Color.black);
        //this.console.setForeground(Color.black);
    }

    private void fireConsoleExecEvent(ConsoleExecEvent event) {
        Object[] ls = this.listeners.getListenerList();
        for (int i = 0; i < ls.length; i = i + 2) {
            if (ls[i] == IConsoleExecListener.class) {
                ((IConsoleExecListener) ls[i + 1]).consoleExecEvent(event);
            }
        }
    }
    
}
