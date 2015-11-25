/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.laboratory.gui;

import org.python.core.PyObject;
import org.python.core.PySystemState;
import org.python.util.PythonInterpreter;

/**
 *
 * @author yaqiang
 */
public class MyPythonInterpreter extends PythonInterpreter{
    /**
     * Constructor
     */
    public MyPythonInterpreter(){
        super();
        this.cflags.source_is_utf8 = true;
    }
    
    /**
     * Constructor
     * @param obj PyObject
     * @param state State
     */
    public MyPythonInterpreter(PyObject obj, PySystemState state){
        super(obj, state);
        this.cflags.source_is_utf8 = true;
    }
}
