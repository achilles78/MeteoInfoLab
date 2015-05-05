/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.meteoinfo.array;

import org.python.core.PyFloat;
import org.python.core.PyInteger;
import org.python.core.PyObject;
import ucar.ma2.Array;
import ucar.ma2.DataType;

/**
 *
 * @author wyq
 */
public class ArrayUtil {

    /**
     * Array range
     *
     * @param start Start value
     * @param stop Stop value
     * @param step Step value
     * @return
     */
    public static Array arrayRange(Object start, Object stop, final Object step) {
        if (stop == null) {
            stop = start;
            start = 0;
        }
        DataType dataType = ArrayUtil.objectsToType(new Object[]{
            start,
            stop,
            step});
        double startv = Double.parseDouble(start.toString());
        double stopv = Double.parseDouble(stop.toString());
        double stepv = Double.parseDouble(step.toString());
        final int length = Math.max(0, (int) Math.ceil((stopv -
                startv) / stepv));
        Array a = Array.factory(dataType, new int[]{length});
        for (int i = 0; i < length; i++) {
            a.setObject(i, i * stepv + startv);
        }
        return a;
    }

    private static DataType objectToType(final Object o) {
        if (o instanceof Integer) {
            return DataType.INT;
        } else if (o instanceof Float) {
            return DataType.FLOAT;
        } else if (o instanceof Double) {
            return DataType.DOUBLE;
        } else {
            return DataType.OBJECT;
        }
    }

    /**
     * Return the appropriate typecode for a PyObject.
     */
    private static DataType objectToType(final PyObject o) {
        if (o instanceof PyInteger) {
            return DataType.INT;
        } else if (o instanceof PyFloat) {
            return DataType.DOUBLE;
        } else {
            return DataType.OBJECT;
        }
    }

    /**
     * Return the number of bytes per element for the given typecode.
     */
    private static short typeToNBytes(final DataType dataType) {
        switch (dataType) {
            case BYTE:
                return 1;
            case SHORT:
                return 2;
            case INT:
            case FLOAT:
                return 4;
            case LONG:
            case DOUBLE:
                return 8;
            case OBJECT:
                return 0;
            default:
                System.out.println("internal error in typeToNBytes");
                return -1;
        }
    }
    
    private static DataType objectsToType(final Object[] objects) {
        if (objects.length == 0) {
            return DataType.INT;
        }
        short new_sz, sz = -1;
        DataType dataType = DataType.INT;
        for (final Object o : objects) {
            final DataType _type = ArrayUtil.objectToType(o);
            new_sz = ArrayUtil.typeToNBytes(_type);
            if (new_sz > sz) {
                dataType = _type;
            }
        }
        return dataType;
    }

    /**
     * Find an appropriate common type for an array of PyObjects.
     */
    private static DataType objectsToType(final PyObject[] objects) {
        if (objects.length == 0) {
            return DataType.INT;
        }
        short new_sz, sz = -1;
        DataType dataType = DataType.INT;
        for (final PyObject o : objects) {
            final DataType _type = ArrayUtil.objectToType(o);
            new_sz = ArrayUtil.typeToNBytes(_type);
            if (new_sz > sz) {
                dataType = _type;
            }
        }
        return dataType;
    }

//    /**
//     * Create a range of numbers in [start, stop) with the given step and
//     * typecode.
//     *
//     * @param start Start of the range (included)
//     * @param stop End of the range (not included)
//     * @param step Stepsize between the start and stop
//     * @return The new multiarray
//     */
//    public static Array arrayRange(PyObject start, PyObject stop, final PyObject step) {
//        if (stop instanceof PyNone) {
//            stop = start;
//            start = Py.Zero;
//        }
//        DataType dataType = ArrayUtil.objectsToType(new PyObject[]{
//            start,
//            stop,
//            step});
//        final int length = Math.max(0, (int) Math.ceil((stop.__float__().getValue() - start.__float__().getValue())
//                / step.__float__().getValue()));
//        Array a = Array.factory(dataType, new int[]{length});
//        for (int i = 0; i < length; i++) {
//            a.setObject(i, i * step.__float__().getValue() + start.__float__().getValue());
//        }
//        return a;
//    }

//    /**
//     * Array range
//     * @param start Start value
//     * @param stop Stop value
//     * @param step Step value
//     * @return 
//     */
//    public static Array arange(final Object start, final Object stop, final Object step){
//        DataType type = DataType.DOUBLE;
//        if (step == null)
//            step = 1;
//        if (start instanceof Integer){
//            if (stop instanceof Integer) {
//                if (step instanceof Integer) {
//                    type = DataType.INT;
//                    start = (int)start;
//                } else if (step instanceof Float) {
//                    type = DataType.FLOAT;
//                } 
//            } else if (stop instanceof Float){
//                if (!(step instanceof Double)){
//                    type = DataType.FLOAT;
//                }
//            }
//        } else if (start instanceof Float) {
//            if (!(stop instanceof Double)) {
//                if (!(step instanceof Double)){
//                    type = DataType.FLOAT;
//                }
//            }
//        }
//        final int length = Math.max(0, (int) Math.ceil((stop - start) / step));
//        Array a = Array.factory(DataType.DOUBLE, new int[] {length});        
//        for (int i = 0; i < length; i++) {
//            a.setObject(i, i * step + start);            
//        }
//        return a;
//    }
}
