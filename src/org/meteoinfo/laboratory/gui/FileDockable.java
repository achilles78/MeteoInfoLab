/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import bibliothek.gui.dock.common.DefaultSingleCDockable;
import bibliothek.gui.dock.common.action.CAction;
import java.io.File;

/**
 *
 * @author wyq
 */
public class FileDockable extends DefaultSingleCDockable {
    
    private final FileExplorer fileExplorer;
    
    public FileDockable(String id, String title, CAction... actions) {
        super(id, title, actions);
        
        fileExplorer = new FileExplorer(null);
        this.getContentPane().add(fileExplorer);
        //this.setCloseable(false);
    }
    
    /**
     * Set path
     * @param path Path
     */
    public void setPath(File path){
        this.fileExplorer.setPath(path);
    }
    
    /**
     * Get FileExplorer
     * @return FileExplorer
     */
    public FileExplorer getFileExplorer(){
        return this.fileExplorer;
    }
}
