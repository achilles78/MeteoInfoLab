/*
 * 01/11/2010
 *
 * Copyright (C) 2011 Robert Futrell
 * robert_futrell at users.sourceforge.net
 * http://fifesoft.com/rsyntaxtextarea
 *
 * This library is distributed under a modified BSD license.  See the included
 * RSTALanguageSupport.License.txt file for details.
 */
package org.meteoinfo.laboratory.codecomplete;

//import javax.swing.ListCellRenderer;

import org.fife.ui.autocomplete.AutoCompletion;
import org.fife.ui.rsyntaxtextarea.RSyntaxTextArea;


/**
 * Language support for Groovy.
 *
 * @author Robert Futrell
 * @version 1.0
 */
public class JythonLanguageSupport extends AbstractLanguageSupport {

	/**
	 * The completion provider, shared amongst all text areas.
	 */
	private JythonCompletionProvider provider;


	/**
	 * Constructor.
	 */
	public JythonLanguageSupport() {
		setParameterAssistanceEnabled(true);
		setShowDescWindow(true);
	}


//	/**
//	 * {@inheritDoc}
//	 */
//	protected ListCellRenderer createDefaultCompletionCellRenderer() {
//		return new CCellRenderer();
//	}


	private JythonCompletionProvider getProvider() {
		if (provider==null) {
			provider = new JythonCompletionProvider();
		}
		return provider;
	}


	/**
	 * {@inheritDoc}
	 */
	@Override
	public void install(RSyntaxTextArea textArea) {

		JythonCompletionProvider provider = getProvider();
		AutoCompletion ac = createAutoCompletion(provider.createCodeCompletionProvider());
		ac.install(textArea);
		installImpl(textArea, ac);

		textArea.setToolTipSupplier(provider);

	}


	/**
	 * {@inheritDoc}
	 */
	@Override
	public void uninstall(RSyntaxTextArea textArea) {
		uninstallImpl(textArea);
	}


}