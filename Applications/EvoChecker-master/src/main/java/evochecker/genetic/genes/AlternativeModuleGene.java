//==============================================================================
//	
 //	Copyright (c) 2015-
//	Authors:
//	* Simos Gerasimou (University of York)
//	
//------------------------------------------------------------------------------
//	
//	This file is part of EvoChecker.
//	
//==============================================================================

package evochecker.genetic.genes;

/**
 * Class representing an alternative module gene
 * @author sgerasimou
 *
 */
public class AlternativeModuleGene extends AbstractGene {

	
	/**
	 * Class constructor
	 * @param name
	 * @param numberOfAlternatives
	 */
	public AlternativeModuleGene(String name, int numberOfAlternatives) {
		super(name, 0, numberOfAlternatives-1, 0);
	}
}
