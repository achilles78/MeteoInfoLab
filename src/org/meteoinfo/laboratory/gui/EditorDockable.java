/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import bibliothek.gui.dock.common.DefaultSingleCDockable;
import bibliothek.gui.dock.common.action.CAction;
import java.awt.Component;
import java.awt.Font;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.PrintStream;
import java.text.MessageFormat;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JOptionPane;
import javax.swing.JTabbedPane;
import javax.swing.JTextArea;
import javax.swing.SwingWorker;
import org.fife.ui.rsyntaxtextarea.SyntaxConstants;
import org.fife.ui.rsyntaxtextarea.TextEditorPane;
import org.meteoinfo.global.GenericFileFilter;
import org.meteoinfo.ui.ButtonTabComponent;
import org.python.util.PythonInterpreter;

/**
 *
 * @author yaqiang
 */
public class EditorDockable extends DefaultSingleCDockable {

    private FrmMain parent;
    //private String startupPath;
    private final JTabbedPane tabbedPanel;
    private Font textFont;

    public EditorDockable(FrmMain parent, String id, String title, CAction... actions) {
        super(id, title, actions);

        this.parent = parent;
        tabbedPanel = new JTabbedPane();
        this.getContentPane().add(tabbedPanel);
        //this.setCloseable(false);
    }

//    /**
//     * Set startup path
//     *
//     * @param path Startup path
//     */
//    public void setStartupPath(String path) {
//        this.startupPath = path;
//    }
    
    /**
     * Get tabbed pane
     * @return Tabbed pane
     */
    public JTabbedPane getTabbedPane(){
        return this.tabbedPanel;
    }

    /**
     * Get font
     *
     * @return Font
     */
    public Font getTextFont() {
        return this.textFont;
    }

    /**
     * Set font
     *
     * @param font Font
     */
    public void setTextFont(Font font) {
        this.textFont = font;
        for (Component tab : this.tabbedPanel.getComponents()) {
            if (tab instanceof TextEditor) {
                ((TextEditor) tab).setTextFont(this.textFont);
            }
        }
    }

    /**
     * Add a new text editor
     *
     * @param title Title
     * @return Text editor
     */
    public final TextEditor addNewTextEditor(String title) {
        final TextEditor tab = new TextEditor(tabbedPanel, title);
        tabbedPanel.add(tab, title);
        tabbedPanel.setSelectedComponent(tab);
        tab.setTextFont(this.textFont);
        tab.getTextArea().setSyntaxEditingStyle(SyntaxConstants.SYNTAX_STYLE_PYTHON);
        tab.getTextArea().discardAllEdits();
        tab.getTextArea().setDirty(false);
        tab.setTitle(title);
        ButtonTabComponent btc = new ButtonTabComponent(tabbedPanel);
        JButton button = btc.getTabButton();
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                closeFile(tab);
            }
        });
        tabbedPanel.setTabComponentAt(tabbedPanel.indexOfComponent(tab), btc);

        return tab;
    }

    /**
     * Get active text editor
     *
     * @return Active text editor
     */
    public TextEditor getActiveTextEditor() {
        if (this.tabbedPanel.getTabCount() == 0) {
            return null;
        } else {
            return (TextEditor) this.tabbedPanel.getSelectedComponent();
        }
    }

    private TextEditorPane getActiveTextArea() {
        TextEditor textEditor = getActiveTextEditor();
        if (textEditor != null) {
            return textEditor.getTextArea();
        } else {
            return null;
        }
    }

    /**
     * Close file
     */
    public void closeFile() {
        closeFile(this.getActiveTextEditor());
    }

    private void closeFile(TextEditor textEditor) {
        //TextEditor textEditor = getActiveTextEditor();
        if (textEditor != null) {
            boolean ifClose = true;
            if (textEditor.getTextArea().isDirty()) {
                String fName = textEditor.getFileName();
                if (fName.isEmpty()) {
                    fName = "New file";
                }
                int result = JOptionPane.showConfirmDialog(null, MessageFormat.format("Save changes to \"{0}\"", fName), "Save?", JOptionPane.YES_NO_CANCEL_OPTION);
                if (result == JOptionPane.YES_OPTION) {
                    if (!doSave(textEditor)) {
                        ifClose = false;
                    }
                } else if (result == JOptionPane.CANCEL_OPTION) {
                    ifClose = false;
                }
            }

            if (ifClose) {
                removeTextEditor(textEditor);
            }
        }
    }

    /**
     * Close all files
     */
    public void closeAllFiles() {
        while (this.tabbedPanel.getTabCount() > 0){
            this.closeFile();
        }
//        for (int i = 0; i < this.tabbedPanel.getTabCount(); i++) {
//            this.closeFile((TextEditor) this.tabbedPanel.getComponentAt(0));
//        }
    }

    /**
     * Save file
     *
     * @param editor The text editor
     * @return Boolean
     */
    public boolean doSave(TextEditor editor) {
        if (editor.getFileName().isEmpty()) {
            return doSaveAs_Jython(editor);
        } else {
            editor.saveFile(editor.getFile());
            return true;
        }
    }

    /**
     * Save as
     *
     * @param editor The text editor
     * @return Boolean
     */
    public boolean doSaveAs_Jython(TextEditor editor) {
        JFileChooser aDlg = new JFileChooser();
        String[] fileExts = new String[]{"py"};
        GenericFileFilter mapFileFilter = new GenericFileFilter(fileExts, "Python File (*.py)");
        aDlg.setFileFilter(mapFileFilter);
        if (editor.getFile() != null) {
            aDlg.setSelectedFile(editor.getFile());
        } else {
            File dir = new File(System.getProperty("user.dir"));
            if (dir.isDirectory()) {
                aDlg.setCurrentDirectory(dir);
            }
        }
        if (aDlg.showSaveDialog(parent) == JFileChooser.APPROVE_OPTION) {
            File file = aDlg.getSelectedFile();
            System.setProperty("user.dir", file.getParent());
            String extent = ((GenericFileFilter) aDlg.getFileFilter()).getFileExtent();
            String fileName = file.getAbsolutePath();
            if (!fileName.substring(fileName.length() - extent.length()).equals(extent)) {
                fileName = fileName + "." + extent;
            }
            file = new File(fileName);
            editor.saveFile(file);
            return true;
        }
        return false;
    }

    private void removeTextEditor(TextEditor editor) {
        this.tabbedPanel.remove(editor);
    }

    /**
     * Open Jython script file
     */
    public void doOpen_Jython() {
        // TODO add your handling code here:          
        JFileChooser aDlg = new JFileChooser();
        aDlg.setMultiSelectionEnabled(true);
        aDlg.setAcceptAllFileFilterUsed(false);
        //File dir = new File(this._parent.getCurrentDataFolder());
        File dir = new File(System.getProperty("user.dir"));
        if (dir.isDirectory()) {
            aDlg.setCurrentDirectory(dir);
        }
        String[] fileExts = new String[]{"py"};
        GenericFileFilter mapFileFilter = new GenericFileFilter(fileExts, "Jython File (*.py)");
        aDlg.setFileFilter(mapFileFilter);
        if (JFileChooser.APPROVE_OPTION == aDlg.showOpenDialog(parent)) {
            File[] files = aDlg.getSelectedFiles();
            //this._parent.setCurrentDataFolder(files[0].getParent());
            System.setProperty("user.dir", files[0].getParent());
            this.openFiles(files);
        }
    }

    /**
     * Open script files
     *
     * @param files The files
     */
    public void openFiles(File[] files) {
        // Close default untitled document if it is still empty
        if (this.tabbedPanel.getTabCount() == 1) {
            TextEditor textEditor = getActiveTextEditor();
            if (textEditor.getTextArea().getDocument().getLength() == 0 && textEditor.getFileName().isEmpty()) {
                this.removeTextEditor(textEditor);
            }
        }

        // Open file(s)
        for (File file : files) {
            boolean isExist = false;
            for (int i = 0; i < this.tabbedPanel.getTabCount(); i++) {
                TextEditor te = (TextEditor) this.tabbedPanel.getComponentAt(i);
                if (file.getAbsolutePath().equals(te.getFileName())) {
                    isExist = true;
                    break;
                }
            }
            if (isExist) {
                continue;
            }
            TextEditor editor = addNewTextEditor(file.getName());
            editor.openFile(file);
        }
    }

    /**
     * Open script file
     *
     * @param file The file
     */
    public void openFile(File file) {
        // Close default untitled document if it is still empty
        if (this.tabbedPanel.getTabCount() == 1) {
            TextEditor textEditor = getActiveTextEditor();
            if (textEditor.getTextArea().getDocument().getLength() == 0 && textEditor.getFileName().isEmpty()) {
                this.removeTextEditor(textEditor);
            }
        }

        // Open file
        boolean isExist = false;
        for (int i = 0; i < this.tabbedPanel.getTabCount(); i++) {
            TextEditor te = (TextEditor) this.tabbedPanel.getComponentAt(i);
            if (file.getAbsolutePath().equals(te.getFileName())) {
                isExist = true;
                break;
            }
        }
        if (!isExist) {
            TextEditor editor = addNewTextEditor(file.getName());
            editor.openFile(file);
        }
    }

    /**
     * Run Jython script
     *
     * @param jTextArea_Output
     */
    public void runPythonScript(final JTextArea jTextArea_Output) {

        SwingWorker worker = new SwingWorker<String, String>() {
            PrintStream oout = System.out;
            PrintStream oerr = System.err;

            @Override
            protected String doInBackground() throws Exception {
                JTextAreaWriter writer = new JTextAreaWriter(jTextArea_Output);
                JTextAreaPrintStream printStream = new JTextAreaPrintStream(System.out, jTextArea_Output);
                jTextArea_Output.setText("");

                // Create an instance of the PythonInterpreter        
                //Py.getSystemState().setdefaultencoding("utf-8");
                //UPythonInterpreter interp = new UPythonInterpreter();
                PythonInterpreter interp = new PythonInterpreter();
                interp.setOut(writer);
                interp.setErr(writer);
                System.setOut(printStream);
                System.setErr(printStream);
                //System.out.println("Out test!");
                //System.err.println("Error test!");

//                boolean isDebug = java.lang.management.ManagementFactory.getRuntimeMXBean().
//                        getInputArguments().toString().contains("jdwp");
                //String pluginPath = startupPath + File.separator + "plugins";
                //List<String> jarfns = GlobalUtil.getFiles(pluginPath, ".jar");
                //String path = startupPath + File.separator + "pylib";
//                if (isDebug) {
//                    path = "D:/MyProgram/Distribution/Java/MeteoInfo/MeteoInfo/pylib";
//                }
                try {
                    interp.exec("import sys");
                    //interp.set("mis", mis);
                    //interp.exec("sys.path.append('" + path + "')");
                    //interp.exec("import mipylib");
                    //interp.exec("from mipylib.miscript import *");                    
                    //interp.exec("from meteoinfo.numeric.JNumeric import *");
                    //interp.exec("mis = MeteoInfoScript()");
                    //interp.set("miapp", _parent);
                    //for (String jarfn : jarfns) {
                    //    interp.exec("sys.path.append('" + jarfn + "')");
                    //}
                } catch (Exception e) {
                    e.printStackTrace();
                }

                TextEditorPane textArea = getActiveTextArea();
                //textArea.setEncoding(fn);
                String code = textArea.getText();
//                if (code.contains("coding=utf-8")){
//                    code = code.replace("coding=utf-8", "coding = utf-8");
//                }
                String encoding = EncodingUtil.findEncoding(code);
                if (encoding != null) {
                    try {
                        interp.execfile(new ByteArrayInputStream(code.getBytes(encoding)));
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                } else {
                    try {
                        interp.execfile(new ByteArrayInputStream(code.getBytes()));
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
//                try {
//                    //interp.exec(code);
//                    interp.execfile(new ByteArrayInputStream(code.getBytes()));
//                } catch (Exception e) {
//                    e.printStackTrace();
//                }

                return "";
            }

            @Override
            protected void done() {
                System.setOut(oout);
                System.setErr(oerr);
            }
        };
        worker.execute();
    }
}
