/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory;

import java.awt.GraphicsEnvironment;
import java.io.File;
import java.util.List;
import java.util.Locale;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.UIManager;
import javax.swing.UnsupportedLookAndFeelException;
import org.meteoinfo.global.util.GlobalUtil;
import org.meteoinfo.laboratory.gui.FrmMain;
import org.python.core.PyString;
import org.python.core.PySystemState;
import org.python.util.InteractiveConsole;
import org.python.util.PythonInterpreter;

/**
 *
 * @author wyq
 */
public class MeteoInfoLab {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        // TODO code application logic here
        if (args.length >= 1) {
            if (args[0].equalsIgnoreCase("-i")) {
                runInteractive();
            } else if (args[0].equalsIgnoreCase("-b")) {
                if (args.length == 1) {
                    System.out.println("Script file name is needed!");
                    System.exit(0);
                } else {
                    String fn = args[1];
                    if (new File(fn).isFile()) {
                        System.setProperty("java.awt.headless", "true");
                        GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
                        System.out.println("Headless mode: " + ge.isHeadless());
                        runScript(args, fn, 1);
                    } else {
                        System.out.println("The script file does not exist!");
                        System.exit(0);
                    }
                }
            } else if (args[0].equalsIgnoreCase("-eng")) {
                runApplication(true);
            } else {
                String fn = args[0];
                if (new File(fn).isFile()) {
                    runScript(args, fn, 0);
                } else {
                    System.out.println("The script file does not exist!");
                    System.exit(0);
                }
            }
        } else {
            runApplication();
        }
    }

    private static void runScript(String args[], String fn, int idx) {
        String ext = GlobalUtil.getFileExtension(fn);
        System.out.println("Running Jython script...");
        PySystemState state = new PySystemState();
        if (args.length > idx + 1) {
            for (int i = idx + 1; i < args.length; i++) {
                state.argv.append(new PyString(args[i]));
            }
        }
        PythonInterpreter interp = new PythonInterpreter(null, state);
        //String pluginPath = GlobalUtil.getAppPath(FrmMain.class) + File.separator + "plugins";
        //List<String> jarfns = GlobalUtil.getFiles(pluginPath, ".jar");
        String path = GlobalUtil.getAppPath(FrmMain.class) + File.separator + "pylib";
        interp.exec("import sys");
        interp.exec("import os");
        interp.exec("sys.path.append('" + path + "')");
        interp.exec("from milab import *");
        interp.exec("mipylib.miplot.batchmode = True");
        interp.exec("mipylib.miplot.isinteractive = False");
//        for (String jarfn : jarfns) {
//            interp.exec("sys.path.append('" + jarfn + "')");            
//        }
        interp.execfile(fn);
        System.exit(0);
    }

    private static void runInteractive() {
//        PlotForm plotForm = new PlotForm();
//        plotForm.setSize(800, 600);
//        plotForm.setVisible(true);
//        MeteoInfoScript mis = new MeteoInfoScript(plotForm);
        String path = GlobalUtil.getAppPath(FrmMain.class) + File.separator + "pylib";
        //MeteoInfoScript mis = new MeteoInfoScript(path);
        InteractiveConsole console = new InteractiveConsole();
        try {
            //console.set("mis", mis);
            console.exec("import sys");
            console.exec("import os");
            console.exec("sys.path.append('" + path + "')");
            console.exec("from milab import *");
            //console.exec("import mipylib");
            //console.exec("from mipylib.miscript import *");
            console.exec("mipylib.miplot.isinteractive = True");
            //console.exec("from meteoinfo.numeric.JNumeric import *");
            //console.exec("import mipylib.miscript as plt");
            //console.exec("import meteoinfo.numeric.JNumeric as np");
            //console.exec("import miscript");
            //console.exec("from miscript import MeteoInfoScript");
            //console.exec("mis = MeteoInfoScript()");
        } catch (Exception e) {
            e.printStackTrace();
        }
        console.interact();
    }
    
    private static void runApplication() {
        runApplication(false);
    }

    private static void runApplication(final boolean isEng) {
        try {
            /* Set look and feel */
            //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
            /* If Nimbus (introduced in Java SE 6) is not available, stay with the default look and feel.
            * For details see http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html
            */
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (ClassNotFoundException | InstantiationException | IllegalAccessException | UnsupportedLookAndFeelException ex) {
            Logger.getLogger(MeteoInfoLab.class.getName()).log(Level.SEVERE, null, ex);
        }
        //</editor-fold>

        /* Create and display the form */
        java.awt.EventQueue.invokeLater(new Runnable() {
            @Override
            public void run() {
//                new Thread() {
//                    @Override
//                    public void run() {
//                        try {
//                            final SplashScreen splash = SplashScreen.getSplashScreen();
//                            if (splash == null){
//                                System.out.println("SplashScreen.getSplashScreen() returned null");
//                                return;
//                            }
//                            Graphics2D g = splash.createGraphics();
//                            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
//                            g.setFont(new Font("Arial", Font.BOLD, 60));
//                            g.setColor(Color.red);
//                            g.drawString("MeteoInfo", 100, 200);
//                            splash.update();
//                            Thread.sleep(1000);
//                            //splash.setImageURL(Program.class.getResource("/meteoinfo/resources/logo.png"));
//                            //splash.update();
//                        } catch (Exception e) {
//                        }
//                    }
//                }.start();

                boolean isDebug = java.lang.management.ManagementFactory.getRuntimeMXBean().
                        getInputArguments().toString().contains("jdwp");
//                if (isDebug) {
//                    Locale.setDefault(Locale.ENGLISH);
//                }

                if (isEng) {
                    Locale.setDefault(Locale.ENGLISH);
                }

                StackWindow sw = null;
                if (!isDebug) {
                    sw = new StackWindow("Show Exception Stack", 600, 400);
                    Thread.UncaughtExceptionHandler handler = sw;
                    Thread.setDefaultUncaughtExceptionHandler(handler);
                    System.setOut(sw.printStream);
                    System.setErr(sw.printStream);
                }

                //registerFonts();
                org.meteoinfo.global.util.FontUtil.registerWeatherFont();
                FrmMain frame = new FrmMain();
                //frame.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
                //frame.setLocationRelativeTo(null);
                frame.setVisible(true);
                if (sw != null) {
                    sw.setLocationRelativeTo(frame);
                }
            }
        });
    }
}
