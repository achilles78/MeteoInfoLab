/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import bibliothek.gui.dock.common.DefaultSingleCDockable;
import bibliothek.gui.dock.common.action.CAction;
import bibliothek.gui.dock.common.action.CButton;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.swing.JButton;
import javax.swing.JTabbedPane;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import org.meteoinfo.chart.ChartPanel;
import org.meteoinfo.chart.MouseMode;
import org.meteoinfo.ui.ButtonTabComponent;

/**
 *
 * @author wyq
 */
public class FigureDockable extends DefaultSingleCDockable {

    private final JTabbedPane tabbedPanel;
    private FrmMain parent;

    public FigureDockable(final FrmMain parent, String id, String title, CAction... actions) {
        super(id, title, actions);

        this.parent = parent;
        tabbedPanel = new JTabbedPane();
        tabbedPanel.addChangeListener(new ChangeListener() {
            @Override
            public void stateChanged(ChangeEvent e) {
                PythonInteractiveInterpreter interp = parent.getConsoleDockable().getInterpreter();
                if (tabbedPanel.getTabCount() == 0) {
                    try {
                        interp.exec("mipylib.miplot.chartpanel = None");
                        interp.exec("mipylib.miplot.c_plot = None");
                    } catch (Exception ex) {
                        ex.printStackTrace();
                    }
                } else {
                    interp.set("cp", tabbedPanel.getSelectedComponent());
                    interp.exec("mipylib.miplot.chartpanel = cp");
                    interp.exec("mipylib.miplot.c_plot = None");
                }
            }
        });
        this.getContentPane().add(tabbedPanel);
        //this.setCloseable(false);
        
        //Add actions     
        //Select action
        CButton button = new CButton();
        button.setText("Select");
        button.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/Arrow.png")));
        button.setTooltip("Select");
        button.addActionListener( new ActionListener(){
            @Override
            public void actionPerformed( ActionEvent e ){
                ChartPanel cp = FigureDockable.this.getCurrentFigure();
                if (cp != null)
                    cp.setMouseMode(MouseMode.SELECT);
            }
        });
        this.addAction(button);
        this.addSeparator();
        //Zoom in action
        button = new CButton();
        button.setText("Zoom In");
        button.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_ZoomIn.Image.png")));
        button.setTooltip("Zoom In");
        button.addActionListener( new ActionListener(){
            @Override
            public void actionPerformed( ActionEvent e ){
                ChartPanel cp = FigureDockable.this.getCurrentFigure();
                if (cp != null)
                    cp.setMouseMode(MouseMode.ZOOM_IN);
            }
        });
        this.addAction(button);
        //Zoom out action
        button = new CButton();
        button.setText("Zoom Out");
        button.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_ZoomOut.Image.png")));
        button.setTooltip("Zoom Out");
        button.addActionListener( new ActionListener(){
            @Override
            public void actionPerformed( ActionEvent e ){
                ChartPanel cp = FigureDockable.this.getCurrentFigure();
                if (cp != null)
                    cp.setMouseMode(MouseMode.ZOOM_OUT);
            }
        });
        this.addAction(button);
        //Pan action
        button = new CButton();
        button.setText("Pan");
        button.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_Pan.Image.png")));
        button.setTooltip("Pan");
        button.addActionListener( new ActionListener(){
            @Override
            public void actionPerformed( ActionEvent e ){
                ChartPanel cp = FigureDockable.this.getCurrentFigure();
                if (cp != null)
                    cp.setMouseMode(MouseMode.PAN);
            }
        });
        this.addAction(button);
        //Full extent action
        button = new CButton();
        button.setText("Full Extent");
        button.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/TSB_FullExtent.Image.png")));
        button.setTooltip("Full Extent");
        button.addActionListener( new ActionListener(){
            @Override
            public void actionPerformed( ActionEvent e ){
                ChartPanel cp = FigureDockable.this.getCurrentFigure();
                if (cp != null)
                    cp.onUndoZoomClick();
            }
        });
        this.addAction(button);
        this.addSeparator();
        //Identifer action
        button = new CButton();
        button.setText("Identifer");
        button.setIcon(new javax.swing.ImageIcon(getClass().getResource("/org/meteoinfo/laboratory/resources/information.png")));
        button.setTooltip("Identifer");
        button.addActionListener( new ActionListener(){
            @Override
            public void actionPerformed( ActionEvent e ){
                ChartPanel cp = FigureDockable.this.getCurrentFigure();
                if (cp != null)
                    cp.setMouseMode(MouseMode.IDENTIFER);
            }
        });
        this.addAction(button);
        this.addSeparator();
    }

    /**
     * Add a new figure
     *
     * @param title Figure title
     * @param cp
     * @return Figure chart panel
     */
    public final ChartPanel addNewFigure(String title, final ChartPanel cp) {
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
     * Add a new figure
     *
     * @param ncp
     * @return Figure chart panel
     */
    public final ChartPanel addFigure(final ChartPanel ncp) {
        int idx = 1;
        if (this.tabbedPanel.getTabCount() > 0) {
            List<Integer> idxes = new ArrayList<>();
            for (int i = 0; i < this.tabbedPanel.getTabCount(); i++) {
                String text = this.tabbedPanel.getTitleAt(i);
                String[] strs = text.split("\\s+");
                if (strs.length > 1) {
                    String idxStr = strs[strs.length - 1];
                    try {
                        idx = Integer.parseInt(idxStr);
                        idxes.add(idx);
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
            Collections.sort(idxes);
            idx = 1;
            boolean isIn = false;
            for (int i : idxes) {
                if (idx < i) {
                    isIn = true;
                    break;
                }
                idx += 1;
            }

            if (!isIn) {
                idx = idxes.size() + 1;
            }
        }

        this.tabbedPanel.add(ncp, "Figure " + String.valueOf(idx));
        this.tabbedPanel.setSelectedComponent(ncp);
        ButtonTabComponent btc = new ButtonTabComponent(tabbedPanel);
        JButton button = btc.getTabButton();
        button.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                tabbedPanel.remove(ncp);
                PythonInteractiveInterpreter interp = parent.getConsoleDockable().getInterpreter();
                if (tabbedPanel.getTabCount() == 0) {
                    try {
                        interp.exec("mipylib.miplot.chartpanel = None");
                        interp.exec("mipylib.miplot.c_plot = None");
                    } catch (Exception ex) {
                        ex.printStackTrace();
                    }
                } else {
                    interp.set("cp", tabbedPanel.getSelectedComponent());
                    interp.exec("mipylib.miplot.chartpanel = cp");
                    interp.exec("mipylib.miplot.c_plot = None");
                }
            }
        });
        tabbedPanel.setTabComponentAt(tabbedPanel.indexOfComponent(ncp), btc);

        return ncp;
    }

    /**
     * Get current figure
     *
     * @return Figure
     */
    public ChartPanel getCurrentFigure() {
        if (this.tabbedPanel.getTabCount() == 0) {
            return null;
        }

        return (ChartPanel) this.tabbedPanel.getSelectedComponent();
    }

    /**
     * Get figure
     *
     * @param idx Figure index
     * @return Figure
     */
    public ChartPanel getFigure(int idx) {
        if (this.tabbedPanel.getTabCount() > idx) {
            return (ChartPanel) this.tabbedPanel.getTabComponentAt(idx);
        } else {
            return null;
        }
    }

    /**
     * Set current figure
     * @param cp ChartPanel
     */
    public void setCurrentFigure(ChartPanel cp){
        if (this.tabbedPanel.getTabCount() > 0){
            this.tabbedPanel.setComponentAt(this.tabbedPanel.getSelectedIndex(), cp);
        }
    }
}
