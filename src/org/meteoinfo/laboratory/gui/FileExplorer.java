/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Toolkit;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.File;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.List;
import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.event.EventListenerList;
import javax.swing.table.DefaultTableModel;
import org.meteoinfo.laboratory.event.CurrentPathChangedEvent;
import org.meteoinfo.laboratory.event.ICurrentPathChangedListener;
import org.meteoinfo.table.IconRenderer;
import org.meteoinfo.table.IconText;

/**
 *
 * @author wyq
 */
public class FileExplorer extends JPanel implements MouseListener{
    
    private final EventListenerList listeners = new EventListenerList();
    //private final JButton jbUp;
    //private final JComboBox jcbPath;
    private final JTable jtFile;
    private final DefaultTableModel dtmFile;
    //private final JLabel jlLocal;
    private File path;
    private String currentPath;
    private int currentIndex;
    private boolean init = false;

    /**
     * Constructor
     * @param path Path
     */
    public FileExplorer(File path) {
        super(new BorderLayout());
        
        this.path = path;
        this.setForeground(Color.white);
        //JPanel jp = new JPanel(new BorderLayout());
        //jbUp = new JButton("Up");
        //jbUp.addActionListener(this);
        //jcbPath = new JComboBox();
        //jcbPath.addActionListener(this);
        //jp.add(jbUp, "West");
        //jp.add(jcbPath, "Center");
        dtmFile = new LocalTableModel();
        dtmFile.addColumn("Name");
        dtmFile.addColumn("Size");
        dtmFile.addColumn("File Type");
        dtmFile.addColumn("Date Modified");
        jtFile = new JTable(dtmFile);
        jtFile.getColumnModel().getColumn(0).setCellRenderer(new IconRenderer());
        jtFile.setShowGrid(false);
        jtFile.addMouseListener(this);
        //jlLocal = new JLabel("本地状态", JLabel.CENTER);

        //add(jp, "North");
        add(new JScrollPane(jtFile), "Center");
        //add(jlLocal, "South");

        //Show current path files
        //path = new File(System.getProperty("user.dir"));
        if (path != null)
            listFiles(path);    

        init = true;
    }
    
    /**
     * Set path
     * @return Path
     */
    public File getPath(){
        return this.path;
    }
    
    /**
     * Set path
     * @param path Path
     */
    public void setPath(File path){
        this.path = path;
        this.listFiles(path);
    }
    
    /**
     * Get table
     * @return Table
     */
    public JTable getTable(){
        return this.jtFile;
    }
    
    public void addCurrentPathChangedListener(ICurrentPathChangedListener listener) {
        this.listeners.add(ICurrentPathChangedListener.class, listener);
    }

    public void removeCurrentPathChangedListener(ICurrentPathChangedListener listener) {
        this.listeners.remove(ICurrentPathChangedListener.class, listener);
    }

    public void fireCurrentPathChangedEvent() {
        fireCurrentPathChangedEvent(new CurrentPathChangedEvent(this));
    }

    private void fireCurrentPathChangedEvent(CurrentPathChangedEvent event) {
        Object[] ls = this.listeners.getListenerList();
        for (int i = 0; i < ls.length; i = i + 2) {
            if (ls[i] == ICurrentPathChangedListener.class) {
                ((ICurrentPathChangedListener) ls[i + 1]).currentPathChangedEvent(event);
            }
        }
    }

    //处理路径的选择事件
//    @Override
//    public void actionPerformed(ActionEvent e) {
//        if (e.getSource()==jbUp && jtFile.getValueAt(0, 0).toString().equals("返回上级")
//                && jtFile.getValueAt(0, 2).toString().equals(""))
//        {
//            listFiles(new File(currentPath).getParentFile());
//            return;
//        }
//        if (init == false)
//        {
//            return;
//        }
//        int index = jcbPath.getSelectedIndex();
//        String item = (String)jcbPath.getSelectedItem();
//        if (item.startsWith("  "))
//        {
//            int root = index - 1;
//            while (((String)jcbPath.getItemAt(root)).startsWith("  "))
//            {
//                root--;
//            }
//            String path = (String)jcbPath.getItemAt(root);
//            while (root < index)
//            {
//                path += ((String)jcbPath.getItemAt(++root)).trim();;
//                path += "\\";
//            }
//            if (listFiles(new File(path)) == false)
//            {
//                jcbPath.setSelectedIndex(currentIndex);
//            }
//            else
//            {
//                currentIndex = index;
//            }
//        }
//        else
//        {
//            if (listFiles(new File(item)) == false)
//            {
//                jcbPath.setSelectedIndex(currentIndex);
//            }
//            else
//            {
//                currentIndex = index;
//            }
//        }
//    }

    //JTable mouse click event
    @Override
    public void mouseClicked(MouseEvent e) {
        if(e.getClickCount()==2) {
            int row = ((JTable)e.getSource()).getSelectedRow();
            if (((JTable)e.getSource()).getValueAt(row, 2).toString().equals("Folder"))
            {
                //Judge if the path is root path
                if (currentPath.split("\\\\").length > 1)
                {
                    this.path = new File(currentPath + "/" + ((JTable)e.getSource()).getValueAt(row, 0).toString());
                }
                else
                {                    
                    this.path = new File(currentPath + ((JTable)e.getSource()).getValueAt(row, 0).toString());
                }
                listFiles(this.path);
                this.fireCurrentPathChangedEvent();
            }
            else if (((JTable)e.getSource()).getValueAt(row, 0).toString().equals("")
                    && ((JTable)e.getSource()).getValueAt(row, 2).toString().equals(""))
            {
                this.path = new File(currentPath).getParentFile();
                listFiles(path);
                this.fireCurrentPathChangedEvent();
            }
        }
    }
    //The not used mouse events
    @Override
    public void mouseEntered(MouseEvent e) {}
    @Override
    public void mouseExited(MouseEvent e) {}
    @Override
    public void mousePressed(MouseEvent e) {}
    @Override
    public void mouseReleased(MouseEvent e) {}

    //Show files
    private boolean listFiles(File path) {        
        String strPath = path.getAbsolutePath();
        if (path.isDirectory() == false)
        {
            JOptionPane.showMessageDialog(this, "The file not exists!");
            return false;
        }
        
        currentPath = path.getAbsolutePath();
        init = false;
        //jcbPath.removeAllItems();
//        File[] roots = File.listRoots();
//        int index = 0;
//        for (int i=0; i<roots.length; i++)
//        {
//            String rootPath = roots[i].getAbsolutePath();
//            //jcbPath.addItem(rootPath);
//            if (currentPath.contains(rootPath))
//            {
//                String[] bufPath = currentPath.split("\\\\");
//                for (int j=1; j<bufPath.length; j++)
//                {
//                    String buf = "  ";
//                    for (int k=1; k<j; k++)
//                    {
//                        buf += "  ";
//                    }
//                    //jcbPath.addItem(buf + bufPath[j]);
//                    index = i + j;
//                }
//                if (bufPath.length == 1)
//                {
//                    index = i;
//                }
//            }
//        }
        //jcbPath.setSelectedIndex(index);
        //init = true;
        //currentIndex = index;

        //Clear
        dtmFile.setRowCount(0);

        //Add "To Parent" line if the path is not root path
        if (strPath.split("\\\\").length > 1)
        {
            java.net.URL imgURL = this.getClass().getResource("/org/meteoinfo/laboratory/resources/previous.png");
            ImageIcon icon = new ImageIcon(imgURL);
            dtmFile.addRow(new Object[]{new IconText(icon, ""), "", "", ""});
        }

        //List all files
        java.net.URL folderURL = this.getClass().getResource("/org/meteoinfo/laboratory/resources/folder.png");
        ImageIcon folderIcon = new ImageIcon(folderURL);
        java.net.URL fileURL = this.getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_NewFile.Image.png");
        ImageIcon fileIcon = new ImageIcon(fileURL);
        File[] files = path.listFiles();
        Arrays.sort(files);
        for (File file : files){
            String name = file.getName();
            if (file.isDirectory()) {
                dtmFile.addRow(new Object[]{new IconText(folderIcon, name), "", "Folder", ""});
            } 
        }
        for (File file : files) {
            String name = file.getName();
            if (file.isFile()) {                              
                if (name.lastIndexOf(".") != -1) {
                    dtmFile.addRow(new Object[]{new IconText(fileIcon, name), sizeFormat(file.length()), name.substring(name.lastIndexOf(".") + 1), new SimpleDateFormat("yyyy/M/d hh:mm").format(new Date(file.lastModified()))});
                } else {
                    dtmFile.addRow(new Object[]{new IconText(fileIcon, name), sizeFormat(file.length()), "", new SimpleDateFormat("yyyy/M/d hh:mm").format(new Date(file.lastModified()))});
                }
            }
        }
        
        //jlLocal.setText(currentPath);

        return true;
    }

    //Convert file size to string
    private String sizeFormat(long length) {
        long kb;
        if (length < 1024)
        {
            return String.valueOf(length);
        }
        else if ((kb = length / 1024) < 1024)
        {
            return (String.valueOf(kb) + "kb");
        }
        else
        {
            return (String.valueOf(length / 1024 / 1024) + "kb");
        }
    }

    //Test
    public static void main(String[] args) {
        JFrame jf = new JFrame("Test");
        jf.setSize(300, 400);
        jf.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        Dimension di = Toolkit.getDefaultToolkit().getScreenSize();
        jf.setLocation((int)(di.getWidth() - jf.getWidth()) / 2, 
                (int)(di.getHeight() - jf.getHeight()) / 2);
        jf.add(new FileExplorer(new File(System.getProperty("user.dir"))));
        jf.setVisible(true);
    }

    //LocalTableModel class
    class LocalTableModel extends DefaultTableModel
    {
        @Override
        public boolean isCellEditable(int row, int column) {
            return false;
        }  
    }
}
