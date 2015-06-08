/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import bibliothek.gui.dock.common.CControl;
import bibliothek.gui.dock.common.CGrid;
import com.l2fprod.common.swing.JFontChooser;
import java.awt.Font;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;
import javax.swing.JFileChooser;
import javax.swing.JTable;
import javax.xml.parsers.ParserConfigurationException;
import org.meteoinfo.chart.ChartPanel;
import org.meteoinfo.laboratory.Options;
import org.meteoinfo.global.util.GlobalUtil;
import org.meteoinfo.laboratory.event.ConsoleExecEvent;
import org.meteoinfo.laboratory.event.CurrentPathChangedEvent;
import org.meteoinfo.laboratory.event.IConsoleExecListener;
import org.meteoinfo.laboratory.event.ICurrentPathChangedListener;
import org.python.core.PyList;
import org.python.core.PyObject;
import org.python.core.PyStringMap;
import org.python.core.PyTuple;
import org.xml.sax.SAXException;

/**
 *
 * @author wyq
 */
public class FrmMain extends javax.swing.JFrame {

    //private final OutputDockable outputDock;
    private final EditorDockable editorDock;
    private final ConsoleDockable consoleDock;
    private final FigureDockable figuresDock;
    private final VariableDockable variableDock;
    private final FileDockable fileDock;
    private String startupPath;
    private Options options = new Options();

    /**
     * Creates new form FrmMain
     */
    public FrmMain() {
        initComponents();

        boolean isDebug = java.lang.management.ManagementFactory.getRuntimeMXBean().
                getInputArguments().toString().contains("jdwp");
        if (isDebug) {
            this.startupPath = System.getProperty("user.dir");
        } else {
            this.startupPath = GlobalUtil.getAppPath(FrmMain.class);
        }

        //Set icon image
        BufferedImage image = null;
        try {
            image = ImageIO.read(this.getClass().getResource("/org/meteoinfo/laboratory/resources/MeteoLab_32.png"));
        } catch (Exception e) {
        }
        this.setIconImage(image);

        //Load configure file
        this.loadConfigureFile();
        this.setLocation(this.options.getMainFormLocation());
        this.setSize(this.options.getMainFormSize());
//        if (isDebug) {
//            this.setSize(1000, 650);
//        } else {
//            this.setSize(this.options.getMainFormSize());
//        }

        //Current folder
        this.jComboBox_CurrentFolder.removeAllItems();
        String cf = this.options.getCurrentFolder();
        if (new File(cf).isDirectory()) {
            this.jComboBox_CurrentFolder.addItem(this.options.getCurrentFolder());
        } else {
            this.jComboBox_CurrentFolder.addItem(this.startupPath);
            this.options.setCurrentFolder(startupPath);
            cf = this.startupPath;
        }

        //Add dockable panels
        CControl control = new CControl(this);
        this.add(control.getContentArea());
        CGrid grid = new CGrid(control);
        //this.outputDock = new OutputDockable("Output", "Output");
        editorDock = new EditorDockable("Editor", "Editor");
        this.editorDock.setStartupPath(startupPath);
        this.editorDock.setTextFont(this.options.getTextFont());
        this.editorDock.addNewTextEditor("New file");
        consoleDock = new ConsoleDockable(this, this.startupPath, "Console", "Console");
        final PythonInteractiveInterpreter interp = this.consoleDock.getInterpreter();
        interp.addConsoleExecListener(new IConsoleExecListener() {
            @Override
            public void consoleExecEvent(ConsoleExecEvent event) {

                PyStringMap locals = (PyStringMap) interp.getLocals();
                PyList items = locals.items();
                String name;
                PyObject var;
                List<Object[]> vars = new ArrayList<>();
                for (Object a : items) {
                    PyTuple at = (PyTuple) a;
                    name = at.__getitem__(0).toString();
                    var = at.__getitem__(1);
                    if (var.toString().contains("<mipylib.dimarray.DimArray instance at")) {
                        vars.add(new Object[]{name, "DimArray", var.__len__(), ""});
                    } else if (var.toString().contains("<mipylib.dimvariable.DimVariable instance at")) {
                        vars.add(new Object[]{name, "DimVariable", var.__len__(), ""});
                    }
                }
                if (FrmMain.this.variableDock != null) {
                    FrmMain.this.variableDock.getVariableExplorer().updateVariables(vars);
                }
            }

        });
        figuresDock = new FigureDockable("Figures", "Figures");
        this.variableDock = new VariableDockable("Variables", "Variable explorer");
        this.fileDock = new FileDockable("Files", "File explorer");
        this.fileDock.setPath(new File(cf));
        this.fileDock.getFileExplorer().addCurrentPathChangedListener(new ICurrentPathChangedListener() {
            @Override
            public void currentPathChangedEvent(CurrentPathChangedEvent event) {
                FrmMain.this.setCurrentPath(FrmMain.this.fileDock.getFileExplorer().getPath().getAbsolutePath());
            }

        });
        this.fileDock.getFileExplorer().getTable().addMouseListener(new MouseAdapter() {

            @Override
            public void mouseClicked(MouseEvent e) {
                if (e.getClickCount() == 2) {
                    int row = ((JTable) e.getSource()).getSelectedRow();
                    if (row >= 0){
                        if (((JTable) e.getSource()).getValueAt(row, 2).toString().equals("py")) {                        
                            File file = new File(FrmMain.this.fileDock.getFileExplorer().getPath().getAbsoluteFile() +
                                    File.separator + ((JTable)e.getSource()).getValueAt(row, 0).toString());
                            FrmMain.this.editorDock.openFile(file);
                        }
                    }
                }
            }

        });
        //grid.add(0, 0, 5, 5, this.outputDock);
        grid.add(0, 0, 5, 5, editorDock);
        grid.add(0, 5, 5, 5, consoleDock);
        grid.add(5, 0, 5, 5, this.variableDock);
        grid.add(5, 0, 5, 5, this.fileDock);
        grid.add(5, 5, 5, 5, figuresDock);
        control.getContentArea().deploy(grid);
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        cControl1 = new bibliothek.gui.dock.common.CControl();
        jPanel_Toolbar = new javax.swing.JPanel();
        jToolBar_Editor = new javax.swing.JToolBar();
        jButton_NewFile = new javax.swing.JButton();
        jButton_OpenFile = new javax.swing.JButton();
        jButton_SaveFile = new javax.swing.JButton();
        jButton_SaveAs = new javax.swing.JButton();
        jSeparator1 = new javax.swing.JToolBar.Separator();
        jButton_Undo = new javax.swing.JButton();
        jButton_Redo = new javax.swing.JButton();
        jSeparator2 = new javax.swing.JToolBar.Separator();
        jButton_RunScript = new javax.swing.JButton();
        jToolBar_CurrentFolder = new javax.swing.JToolBar();
        jLabel1 = new javax.swing.JLabel();
        jComboBox_CurrentFolder = new javax.swing.JComboBox();
        jButton_CurrentFolder = new javax.swing.JButton();
        jPanel_Status = new javax.swing.JPanel();
        jMenuBar1 = new javax.swing.JMenuBar();
        jMenu_File = new javax.swing.JMenu();
        jMenuItem_Exist = new javax.swing.JMenuItem();
        jMenu_Editor = new javax.swing.JMenu();
        jMenuItem_Cut = new javax.swing.JMenuItem();
        jMenuItem_Copy = new javax.swing.JMenuItem();
        jMenuItem_Paste = new javax.swing.JMenuItem();
        jMenu_Options = new javax.swing.JMenu();
        jMenuItem_SetFont = new javax.swing.JMenuItem();
        jMenu_Help = new javax.swing.JMenu();
        jMenuItem_About = new javax.swing.JMenuItem();

        setDefaultCloseOperation(javax.swing.WindowConstants.EXIT_ON_CLOSE);
        setTitle("MeteoInfoLab");
        addWindowListener(new java.awt.event.WindowAdapter() {
            public void windowClosing(java.awt.event.WindowEvent evt) {
                formWindowClosing(evt);
            }
        });

        jPanel_Toolbar.setLayout(new java.awt.BorderLayout());

        jToolBar_Editor.setRollover(true);
        jToolBar_Editor.setPreferredSize(new java.awt.Dimension(220, 25));

        jButton_NewFile.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_NewFile.Image.png"))); // NOI18N
        jButton_NewFile.setToolTipText("New File");
        jButton_NewFile.setFocusable(false);
        jButton_NewFile.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_NewFile.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_NewFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_NewFileActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_NewFile);

        jButton_OpenFile.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/Folder_1_16x16x8.png"))); // NOI18N
        jButton_OpenFile.setToolTipText("Open File");
        jButton_OpenFile.setFocusable(false);
        jButton_OpenFile.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_OpenFile.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_OpenFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_OpenFileActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_OpenFile);

        jButton_SaveFile.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/Disk_1_16x16x8.png"))); // NOI18N
        jButton_SaveFile.setToolTipText("Save File");
        jButton_SaveFile.setFocusable(false);
        jButton_SaveFile.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_SaveFile.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_SaveFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_SaveFileActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_SaveFile);

        jButton_SaveAs.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/save_16.png"))); // NOI18N
        jButton_SaveAs.setToolTipText("Save As");
        jButton_SaveAs.setFocusable(false);
        jButton_SaveAs.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_SaveAs.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_SaveAs.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_SaveAsActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_SaveAs);
        jToolBar_Editor.add(jSeparator1);

        jButton_Undo.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_Undo.Image.png"))); // NOI18N
        jButton_Undo.setToolTipText("Undo");
        jButton_Undo.setFocusable(false);
        jButton_Undo.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_Undo.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_Undo.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_UndoActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_Undo);

        jButton_Redo.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_Redo.Image.png"))); // NOI18N
        jButton_Redo.setToolTipText("Redo");
        jButton_Redo.setFocusable(false);
        jButton_Redo.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_Redo.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_Redo.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_RedoActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_Redo);
        jToolBar_Editor.add(jSeparator2);

        jButton_RunScript.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_RunScript.Image.png"))); // NOI18N
        jButton_RunScript.setToolTipText("Run Script");
        jButton_RunScript.setFocusable(false);
        jButton_RunScript.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_RunScript.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_RunScript.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_RunScriptActionPerformed(evt);
            }
        });
        jToolBar_Editor.add(jButton_RunScript);

        jPanel_Toolbar.add(jToolBar_Editor, java.awt.BorderLayout.LINE_START);

        jToolBar_CurrentFolder.setRollover(true);

        jLabel1.setText("Current Folder:");
        jToolBar_CurrentFolder.add(jLabel1);

        jComboBox_CurrentFolder.setEditable(true);
        jComboBox_CurrentFolder.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Item 1", "Item 2", "Item 3", "Item 4" }));
        jComboBox_CurrentFolder.setPreferredSize(new java.awt.Dimension(300, 21));
        jComboBox_CurrentFolder.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jComboBox_CurrentFolderActionPerformed(evt);
            }
        });
        jToolBar_CurrentFolder.add(jComboBox_CurrentFolder);

        jButton_CurrentFolder.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/folder.png"))); // NOI18N
        jButton_CurrentFolder.setFocusable(false);
        jButton_CurrentFolder.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButton_CurrentFolder.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jButton_CurrentFolder.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton_CurrentFolderActionPerformed(evt);
            }
        });
        jToolBar_CurrentFolder.add(jButton_CurrentFolder);

        jPanel_Toolbar.add(jToolBar_CurrentFolder, java.awt.BorderLayout.LINE_END);

        getContentPane().add(jPanel_Toolbar, java.awt.BorderLayout.NORTH);

        jPanel_Status.setPreferredSize(new java.awt.Dimension(588, 25));

        javax.swing.GroupLayout jPanel_StatusLayout = new javax.swing.GroupLayout(jPanel_Status);
        jPanel_Status.setLayout(jPanel_StatusLayout);
        jPanel_StatusLayout.setHorizontalGroup(
            jPanel_StatusLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 699, Short.MAX_VALUE)
        );
        jPanel_StatusLayout.setVerticalGroup(
            jPanel_StatusLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGap(0, 25, Short.MAX_VALUE)
        );

        getContentPane().add(jPanel_Status, java.awt.BorderLayout.PAGE_END);

        jMenu_File.setText("File");

        jMenuItem_Exist.setText("Exist");
        jMenuItem_Exist.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem_ExistActionPerformed(evt);
            }
        });
        jMenu_File.add(jMenuItem_Exist);

        jMenuBar1.add(jMenu_File);

        jMenu_Editor.setMnemonic('E');
        jMenu_Editor.setText("Edit");

        jMenuItem_Cut.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_X, java.awt.event.InputEvent.CTRL_MASK));
        jMenuItem_Cut.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSMI_EditCut.Image.png"))); // NOI18N
        jMenuItem_Cut.setText("Cut");
        jMenuItem_Cut.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem_CutActionPerformed(evt);
            }
        });
        jMenu_Editor.add(jMenuItem_Cut);

        jMenuItem_Copy.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_C, java.awt.event.InputEvent.CTRL_MASK));
        jMenuItem_Copy.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/menuEditCopy.Image.png"))); // NOI18N
        jMenuItem_Copy.setText("Copy");
        jMenuItem_Copy.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem_CopyActionPerformed(evt);
            }
        });
        jMenu_Editor.add(jMenuItem_Copy);

        jMenuItem_Paste.setAccelerator(javax.swing.KeyStroke.getKeyStroke(java.awt.event.KeyEvent.VK_V, java.awt.event.InputEvent.CTRL_MASK));
        jMenuItem_Paste.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/pasteToolStripButton.Image.png"))); // NOI18N
        jMenuItem_Paste.setText("Paste");
        jMenuItem_Paste.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem_PasteActionPerformed(evt);
            }
        });
        jMenu_Editor.add(jMenuItem_Paste);

        jMenuBar1.add(jMenu_Editor);

        jMenu_Options.setMnemonic('O');
        jMenu_Options.setText("Options");

        jMenuItem_SetFont.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/miSetFont.Image.png"))); // NOI18N
        jMenuItem_SetFont.setText("Set Font");
        jMenuItem_SetFont.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem_SetFontActionPerformed(evt);
            }
        });
        jMenu_Options.add(jMenuItem_SetFont);

        jMenuBar1.add(jMenu_Options);

        jMenu_Help.setText("Help");

        jMenuItem_About.setText("About");
        jMenuItem_About.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jMenuItem_AboutActionPerformed(evt);
            }
        });
        jMenu_Help.add(jMenuItem_About);

        jMenuBar1.add(jMenu_Help);

        setJMenuBar(jMenuBar1);

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void jButton_NewFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_NewFileActionPerformed
        // TODO add your handling code here:
        this.editorDock.addNewTextEditor("New file");
    }//GEN-LAST:event_jButton_NewFileActionPerformed

    private void jButton_OpenFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_OpenFileActionPerformed
        // TODO add your handling code here:
        this.editorDock.doOpen_Jython(this);
    }//GEN-LAST:event_jButton_OpenFileActionPerformed

    private void jButton_SaveFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_SaveFileActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        if (textEditor != null) {
            this.editorDock.doSave(textEditor);
        }
    }//GEN-LAST:event_jButton_SaveFileActionPerformed

    private void jButton_UndoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_UndoActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        textEditor.getTextArea().undoLastAction();
    }//GEN-LAST:event_jButton_UndoActionPerformed

    private void jButton_RedoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_RedoActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        textEditor.getTextArea().redoLastAction();
    }//GEN-LAST:event_jButton_RedoActionPerformed

    private void jButton_RunScriptActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_RunScriptActionPerformed
        TextEditor te = this.editorDock.getActiveTextEditor();
        if (!te.getFileName().isEmpty()) {
            te.saveFile(te.getFile());
        }
        
        String code = te.getTextArea().getText();
        //this.consoleDock.runfile(te.getTextArea().getText());
        //this.consoleDock.exec(te.getTextArea().getText());
        this.consoleDock.runPythonScript(code);
//        if (!te.getFileName().isEmpty()) {
//            te.saveFile(te.getFile());
//            try {
//                String fn = te.getFile().getCanonicalPath();
//                String backslash= System.getProperty("file.separator") ;
//                fn = fn.replace(backslash,"/");
//                //fn = fn.replaceAll("\\", "/");
//                this.consoleDock.run("execfile('" + fn + "')");
//            } catch (IOException ex) {
//                Logger.getLogger(FrmMain.class.getName()).log(Level.SEVERE, null, ex);
//            }            
//        } else {
//            //this.consoleDock.exec(te.getTextArea().getText());
//            this.consoleDock.runfile(te.getTextArea().getText());
//        }

        //this.editor.runPythonScript();        
    }//GEN-LAST:event_jButton_RunScriptActionPerformed

    private void formWindowClosing(java.awt.event.WindowEvent evt) {//GEN-FIRST:event_formWindowClosing
        // TODO add your handling code here:
        this.saveConfigureFile();
    }//GEN-LAST:event_formWindowClosing

    private void jButton_SaveAsActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_SaveAsActionPerformed
        // TODO add your handling code here:
        TextEditor editor = this.editorDock.getActiveTextEditor();
        if (editor != null) {
            this.editorDock.doSaveAs_Jython(editor);
        }
    }//GEN-LAST:event_jButton_SaveAsActionPerformed

    private void jMenuItem_SetFontActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem_SetFontActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        Font tFont = JFontChooser.showDialog(this, null, textEditor.getTextArea().getFont());
        if (tFont != null) {
            this.editorDock.setTextFont(tFont);
            this.options.setTextFont(tFont);
        }
    }//GEN-LAST:event_jMenuItem_SetFontActionPerformed

    private void jMenuItem_CutActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem_CutActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        textEditor.getTextArea().cut();
    }//GEN-LAST:event_jMenuItem_CutActionPerformed

    private void jMenuItem_CopyActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem_CopyActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        textEditor.getTextArea().copy();
    }//GEN-LAST:event_jMenuItem_CopyActionPerformed

    private void jMenuItem_PasteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem_PasteActionPerformed
        // TODO add your handling code here:
        TextEditor textEditor = this.editorDock.getActiveTextEditor();
        textEditor.getTextArea().paste();
    }//GEN-LAST:event_jMenuItem_PasteActionPerformed

    private void jMenuItem_AboutActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem_AboutActionPerformed
        // TODO add your handling code here:
        FrmAbout frmAbout = new FrmAbout(this, false);
        frmAbout.setLocationRelativeTo(this);
        frmAbout.setVisible(true);
    }//GEN-LAST:event_jMenuItem_AboutActionPerformed

    private void jComboBox_CurrentFolderActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jComboBox_CurrentFolderActionPerformed
        // TODO add your handling code here:   
        if (this.fileDock == null) {
            return;
        }

        if (this.jComboBox_CurrentFolder.getItemCount() > 0) {
            String path = this.jComboBox_CurrentFolder.getSelectedItem().toString();
            if (new File(path).isDirectory()) {
                this.fileDock.setPath(new File(path));
            }
        }
    }//GEN-LAST:event_jComboBox_CurrentFolderActionPerformed

    private void jButton_CurrentFolderActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton_CurrentFolderActionPerformed
        // TODO add your handling code here:
        JFileChooser aDlg = new JFileChooser();
        //String path = System.getProperty("user.dir");
        File pathDir = new File(this.jComboBox_CurrentFolder.getSelectedItem().toString());
        if (pathDir.isDirectory()) {
            aDlg.setCurrentDirectory(pathDir);
        }
        aDlg.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        if (JFileChooser.APPROVE_OPTION == aDlg.showOpenDialog(this)) {
            File aFile = aDlg.getSelectedFile();
            String path = aFile.getAbsolutePath();
            this.setCurrentPath(path);
            this.fileDock.setPath(new File(this.options.getCurrentFolder()));
        }
    }//GEN-LAST:event_jButton_CurrentFolderActionPerformed

    private void jMenuItem_ExistActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jMenuItem_ExistActionPerformed
        // TODO add your handling code here:
        this.dispose();
    }//GEN-LAST:event_jMenuItem_ExistActionPerformed

    /**
     * Get figure dockable
     *
     * @return Figure dockable
     */
    public FigureDockable getFigureDock() {
        return this.figuresDock;
    }
    
    /**
     * Get current folder
     * @return Current folder
     */
    public String getCurrentFolder(){
        return this.options.getCurrentFolder();
    }

    /**
     * Get console dockable
     *
     * @return Console dockable
     */
    public ConsoleDockable getConsoleDockable() {
        return this.consoleDock;
    }

    /**
     * Load configure file
     */
    public final void loadConfigureFile() {
        String fn = this.startupPath + File.separator + "milconfig.xml";
        if (new File(fn).exists()) {
            try {
                this.options.loadConfigFile(fn);
            } catch (SAXException | IOException | ParserConfigurationException ex) {
                Logger.getLogger(FrmMain.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    }

    /**
     * Save configure file
     */
    public final void saveConfigureFile() {
        String fn = this.options.getFileName();
        try {
            this.options.setMainFormLocation(this.getLocation());
            this.options.setMainFormSize(this.getSize());
            this.options.saveConfigFile(fn);
        } catch (ParserConfigurationException ex) {
            Logger.getLogger(FrmMain.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    /**
     * Set current path
     *
     * @param path Current path
     */
    public void setCurrentPath(String path) {
        this.options.setCurrentFolder(path);
        List<String> paths = new ArrayList<>();
        if (this.jComboBox_CurrentFolder.getItemCount() > 10) {
            this.jComboBox_CurrentFolder.removeItemAt(0);
        }
        for (int i = 0; i < this.jComboBox_CurrentFolder.getItemCount(); i++) {
            paths.add(this.jComboBox_CurrentFolder.getItemAt(i).toString());
        }
        if (!paths.contains(path)) {
            this.jComboBox_CurrentFolder.addItem(path);
        }
        this.jComboBox_CurrentFolder.setSelectedItem(path);
        
        PythonInteractiveInterpreter interp = this.consoleDock.getInterpreter();
        try {
            interp.exec("mipylib.midata.currentfolder = '" + path + "'");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * @param args the command line arguments
     */
    public static void main(String args[]) {
        /* Set the Nimbus look and feel */
        //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
        /* If Nimbus (introduced in Java SE 6) is not available, stay with the default look and feel.
         * For details see http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html 
         */
        try {
            for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels()) {
                if ("Nimbus".equals(info.getName())) {
                    javax.swing.UIManager.setLookAndFeel(info.getClassName());
                    break;
                }
            }
        } catch (ClassNotFoundException ex) {
            java.util.logging.Logger.getLogger(FrmMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        } catch (InstantiationException ex) {
            java.util.logging.Logger.getLogger(FrmMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        } catch (IllegalAccessException ex) {
            java.util.logging.Logger.getLogger(FrmMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        } catch (javax.swing.UnsupportedLookAndFeelException ex) {
            java.util.logging.Logger.getLogger(FrmMain.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
        }
        //</editor-fold>

        /* Create and display the form */
        java.awt.EventQueue.invokeLater(new Runnable() {
            @Override
            public void run() {
                new FrmMain().setVisible(true);
            }
        });
    }

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private bibliothek.gui.dock.common.CControl cControl1;
    private javax.swing.JButton jButton_CurrentFolder;
    private javax.swing.JButton jButton_NewFile;
    private javax.swing.JButton jButton_OpenFile;
    private javax.swing.JButton jButton_Redo;
    private javax.swing.JButton jButton_RunScript;
    private javax.swing.JButton jButton_SaveAs;
    private javax.swing.JButton jButton_SaveFile;
    private javax.swing.JButton jButton_Undo;
    private javax.swing.JComboBox jComboBox_CurrentFolder;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JMenuBar jMenuBar1;
    private javax.swing.JMenuItem jMenuItem_About;
    private javax.swing.JMenuItem jMenuItem_Copy;
    private javax.swing.JMenuItem jMenuItem_Cut;
    private javax.swing.JMenuItem jMenuItem_Exist;
    private javax.swing.JMenuItem jMenuItem_Paste;
    private javax.swing.JMenuItem jMenuItem_SetFont;
    private javax.swing.JMenu jMenu_Editor;
    private javax.swing.JMenu jMenu_File;
    private javax.swing.JMenu jMenu_Help;
    private javax.swing.JMenu jMenu_Options;
    private javax.swing.JPanel jPanel_Status;
    private javax.swing.JPanel jPanel_Toolbar;
    private javax.swing.JToolBar.Separator jSeparator1;
    private javax.swing.JToolBar.Separator jSeparator2;
    private javax.swing.JToolBar jToolBar_CurrentFolder;
    private javax.swing.JToolBar jToolBar_Editor;
    // End of variables declaration//GEN-END:variables
}
