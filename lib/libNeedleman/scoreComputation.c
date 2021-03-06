// -*- coding: utf-8 -*-

//+---------------------------------------------------------------------------+
//|          01001110 01100101 01110100 01111010 01101111 01100010            |
//|                                                                           |
//|               Netzob : Inferring communication protocols                  |
//+---------------------------------------------------------------------------+
//| Copyright (C) 2011 Georges Bossert and Frédéric Guihéry                   |
//| This program is free software: you can redistribute it and/or modify      |
//| it under the terms of the GNU General Public License as published by      |
//| the Free Software Foundation, either version 3 of the License, or         |
//| (at your option) any later version.                                       |
//|                                                                           |
//| This program is distributed in the hope that it will be useful,           |
//| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
//| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
//| GNU General Public License for more details.                              |
//|                                                                           |
//| You should have received a copy of the GNU General Public License         |
//| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
//+---------------------------------------------------------------------------+
//| @url      : http://www.netzob.org                                         |
//| @contact  : contact@netzob.org                                            |
//| @sponsors : Amossys, http://www.amossys.fr                                |
//|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
//+---------------------------------------------------------------------------+

//Compilation Windows
//cl -Fe_libScoreComputation.pyd -Ox -Ot -openmp -LD /I"C:\Python26\include" /I"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\include" libScoreComputation.c "C:\Python26\libs\python26.lib" "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\lib\vcomp.lib"

//+---------------------------------------------------------------------------+
//| Import Associated Header
//+---------------------------------------------------------------------------+
#include "scoreComputation.h"
#ifdef _WIN32
#include <stdio.h>
#include <malloc.h>
#endif

/* float NeedlemanScore(t_message * message1, t_message * message2, Bool debugMode); */

/* /\** */
/*    NeedlemanScore: */

/*    Computes the similarity score between two messages */
/*    @param message1, messages2 : the two messages to compare */
/*    @param debugMode: activate/deactivate the debug messages */
/*    @return a float representing the similarity based on an alignment score */
/* *\/ */
/* float NeedlemanScore(t_message * message1, t_message * message2, Bool debugMode) { */
/*   // local variables */
/*   unsigned int **matrix; */
/*   unsigned int i = 0; */
/*   unsigned int j = 0; */

/*   // Construction of the matrix */
/*   int elt1, elt2, elt3, max; */
/*   // Levenshtein distance */
/*   float levenshtein = 0.0; */
/*   unsigned int maxLen = 0; */

/*   //+------------------------------------------------------------------------+ */
/*   // Create and initialize the matrix */
/*   //+------------------------------------------------------------------------+ */
/*   matrix = (unsigned int**) malloc( */
/* 				   sizeof(unsigned int*) * (message1->len + 1)); */
/*   for (i = 0; i < (message1->len + 1); i++) { */
/*     matrix[i] = (unsigned int*) calloc((message2->len + 1), */
/* 				       sizeof(unsigned int)); */
/*     memset(matrix[i], 0, (message2->len + 1)); */
/*   } */

/*   //+------------------------------------------------------------------------+ */
/*   // Fullfill the matrix given the two messages */
/*   //+------------------------------------------------------------------------+ */
/*   // Parralelization: */
/*   unsigned int nbDiag = 0; // Total number of diagonals */
/*   unsigned int nbBlock = 0; // Effective Number of blocks on the current diagonal - 1 */
/*   unsigned int minLen = 0; */
/*   unsigned int firsti = 0; */
/*   unsigned int firstj = 0; */
/*   unsigned int diagloop = 0; */
/*   unsigned int blockLoop = 0; */
/*   unsigned int lastRow = 0; */
/*   unsigned int lastColumn = 0; */
/*   unsigned int iblock = 0; */
/*   unsigned int jblock = 0; */
/*   unsigned int maxLoopi = 0; */
/*   unsigned int maxLoopj = 0; */

/*   lastRow = ((message1->len + 1) / BLEN) * BLEN; */
/*   lastColumn = ((message2->len + 1) / BLEN) * BLEN; */

/*   nbDiag = (message1->len + 1) / BLEN + (message2->len + 1) / BLEN */
/*     + ((message1->len + 1) % BLEN != 0); // reminder: BLEN = blocklength */

/*   minLen = */
/*     message1->len + 1 <= message2->len + 1 ? */
/*     message1->len + 1 : message2->len + 1; */
/*   maxLen = */
/*     message1->len + 1 > message2->len + 1 ? */
/*     message1->len + 1 : message2->len + 1; */

/*   // Begin loop over diagonals */
/*   for (diagloop = 0; diagloop < nbDiag; diagloop++) { */
/*     //printf("Diag n %d\n",diagloop); */
/*     for (blockLoop = 0; blockLoop <= nbBlock; blockLoop++) { */
/*       //printf("Block n %d\n",blockLoop); */
/*       //(iblock,jblock are moving from the bottom left of the current diagonal to the top right) */
/*       iblock = firsti - blockLoop * BLEN; */
/*       jblock = firstj + blockLoop * BLEN; */
/*       maxLoopi = */
/* 	iblock + BLEN <= message1->len + 1 ? */
/* 	iblock + BLEN : message1->len + 1; */
/*       maxLoopj = */
/* 	jblock + BLEN <= message2->len + 1 ? */
/* 	jblock + BLEN : message2->len + 1; */

/*       for (i = iblock; i < maxLoopi; i++) { */
/* 	for (j = jblock; j < maxLoopj; j++) { */
/* 	  if (i > 0 && j > 0) { */
/* 	    elt1 = matrix[i - 1][j - 1]; */
/* 	    if ((message1->mask[i - 1] == 0) */
/* 		&& (message2->mask[j - 1] == 0) */
/* 		&& (message1->alignment[i - 1] */
/* 		    == message2->alignment[j - 1])) { */
/* 	      //printf("++++++++++++%02x %02x\n",message1->alignment[i - 1],message2->alignment[j - 1]); */
/* 	      elt1 += MATCH; */
/* 	    } else { */
/* 	      //printf("------------%02x %02x\n",message1->alignment[i - 1],message2->alignment[j - 1]); */
/* 	      elt1 += MISMATCH; */
/* 	    } */
/* 	    elt2 = matrix[i][j - 1] + GAP; */
/* 	    elt3 = matrix[i - 1][j] + GAP; */
/* 	    max = elt1 > elt2 ? elt1 : elt2; */
/* 	    max = max > elt3 ? max : elt3; */
/* 	    matrix[i][j] = max; */

/* 	  }	  //printf("%d,\t",matrix[i][j]); */
/* 	} */
/* 	//printf("\n"); */
/*       }	  //End for iblock */
/*     }	  //End for blockLoop */

/*     //Actualize the number of block for the next time */
/*     if (diagloop < minLen / BLEN) { */
/*       nbBlock++; */
/*     } else if (diagloop > maxLen / BLEN) { */
/*       nbBlock--; */
/*     } */

/*     //Actualise the first position of the cursor (bottom left of the next diagonal) */
/*     if (firsti != lastRow) // If we are not at the last row */
/*       firsti = firsti + BLEN; */

/*     else if (firstj != lastColumn) // Else If we are not at the last column */
/*       firstj += BLEN; */

/*   } //End for diagloop */

/*   levenshtein = MATCH * (float) matrix[message1->len][message2->len] / maxLen; */
/*   // Room service */
/*   for (i = 0; i < (message1->len + 1); i++) { */
/*     free(matrix[i]); */
/*   } */
/*   free(matrix); */
/*   if (debugMode) { */
/*     printf("score %lf\n",levenshtein); */
/*   } */
/*   return levenshtein; */
/* } */

/**
   computeSimilarityMatrix:

   This functions computes a matrix which contains the similarity scores
   between the provided messages
   @param nbMessage: the number of provided messages in the param messages
   @param messages: a list containing messages to work with
   @param debug: activate or deactive debug messages
   @param scoreMatrix: a double-dimension array where the matrix score will be stored
*/
void computeSimilarityMatrix(int nbMessage, t_message* messages, Bool debugMode, float** scoreMatrix) {
  int i;
  t_message tmpResultMessage;
  t_score score;

  // local variable
  int p = 0;

  /**
     Stops the execution if user requested so
  */
  if (callbackIsFinish() == 1) {
    return;
  }

  /**
     We loop over each different couple of messages
     messages[i] and messages [p] with i < p
     (diag. superior matrix)
  */
  for (i = 0; i < nbMessage; i++) {
    /**
     Stops the execution if user requested so
    */
    if (callbackIsFinish() == 1) {
      return;
    }

    for (p = i + 1; p < nbMessage; p++) {
      /**
	 Computes the NeedlemanScore between messages i and p
	 result is stored in the matrix[i][p]
      */
      tmpResultMessage.len = 0;
      score.s1 = 0;
      score.s2 = 0;
      score.s3 = 0;
      tmpResultMessage.score = &score;

      char * regex = alignTwoMessages(&tmpResultMessage, FALSE, &messages[i], &messages[p], debugMode);
      if (debugMode) {
		printf("Regex = %s\n", regex);
      }
      free(regex);
      scoreMatrix[i][p] = computeDistance(tmpResultMessage.score);
    }

    /**
       Update the current status
    */
    double val = (double) 100.0 * (i * nbMessage + nbMessage - 1) / ((nbMessage - 1) * (nbMessage + 1));
    if (callbackStatus(0,val,"Building Status (%.2lf %%)",(float) val) == -1) {
      printf("Error, error while executing C callback.\n");
    }
  }

}
