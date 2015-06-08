/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import bibliothek.gui.dock.common.DefaultSingleCDockable;
import bibliothek.gui.dock.common.action.CAction;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.JButton;
import javax.swing.JTabbedPane;
import org.meteoinfo.chart.ChartPanel;
import org.meteoinfo.ui.ButtonTabComponent;

/**
 *
 * @author wyq
 */
public class FigureDockable extends DefaultSingleCDockable{

    private final JTabbedPane tabbedPanel;
    
    public FigureDockable(String id, String title, CAction... actions) {
        super(id, title, actions);
        
        tabbedPanel = new JTabbedPane(); 
        this.getContentPane().add(tabbedPanel);
        //this.setCloseable(false);
    }
    
    /**
     * Add a new figure
     * @param title Figure title
     * @param cp
     * @return Figure chart panel
     */
    public final ChartPanel addNewFigure(String title, final ChartPanel cp){        
        this.tabbedPanel.add(cp, title);
        this.tabbedPanel.setSelectedComponent(cp);
        ButtonTabComponent btc = new ButtonTabComponent(tabbedPanel);
        JButton button = btc.getTabButton();
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                tabbedPanel.remove(cp);
            }
        });
        tabbedPanel.setTabComponentAt(tabbedPanel.indexOfComponent(cp), btc);

        return cp;
    }
    
    /**
     * Get current figure
     * @return Figure
     */
    public ChartPanel getCurrentFigure(){        
        if (this.tabbedPanel.getTabCount() == 0)
            return null;
        
        return (ChartPanel)this.tabbedPanel.getSelectedComponent();
    }

    /**
     * Get figure
     * @param idx Figure index
     * @return Figure
     */
    public ChartPanel getFigure(int idx){
        if (this.tabbedPanel.getTabCount() > idx){
            return (ChartPanel)this.tabbedPanel.getTabComponentAt(idx);
        } else {
            return null;
        }
    }
    
}
