# Codon optimizer

<br>

## Overview
This program allows you to perform codon optimization for multiple species at once, starting from an amino acid sequence or a coding DNA sequence. The program considers the species you select and the cut sites you want to avoid as well as some other problematic characteristics and outputs an optimized DNA sequence.

<br>

## Usage
### Species weights
By selecting the checkbox, you can see all of the species you can optimize for. A species with a weight of zero won't be considered, while all larger numbers will be given proportional consideration. All of the weights are added together, and each species contributes as a proportion of its weight divided by the total.
### Restriction sites
By selecting the checkbox, you can see all of the restriction enzyme cut sites you can choose to avoid. Selecting a large number may result in too much rare codon usage or a failure to avoid a site, but both will be recognizable in the color coding of the generated sequence.
### "DNA here" box
Paste in the coding sequence you want to be optimized (preferably including the stop codon), and the program will convert it into amino acids and then back into an optimized DNA sequence for you to use.
### "Amino acids here" box
Paste in the 1-letter amino acid sequence of your protein of interest (preferably with a stop codon represented as an asterisk), and the program will generate a DNA sequence optimized for your organism(s) of interest.
### "Show codon preferences" button
This gives you a preview of the aspirational percentages of codon usage that will be utilized while generating the optimized DNA sequence. This first value after the codon can be compared to the species-specific preferences following it to help you determine how you may want to adjust your weights.
### "Optimize" button
This begins the optimization process. You should expect it to take several seconds.

<br>

## Interpreting the output
### WARNING
For some sequences, the output appears to be almost twice as long as expected for an unknown reason. Changing the sequence (such as by adding or removing a stop codon) seems to sidestep the issue for the time being.
### Score
The score shows the quality of the sequence, especially with the ability to avoid undesirable sequences. A perfect score is very difficult to attain, but that doesn't mean a useful sequence is very difficult to attain.
### GC content
The GC content helps you double-check the sequence viability. Unsurprisingly, it tells you the percentage of the sequence which consists of guanine or cytosine.
### Color coding
The output should be primarily green with occasional blue and a proportional gradient in between. These colors represent the average prevalence of the codons across your selected species. Abundant blue suggests a sequence that is likely to have translation difficulties. Orange or red shouldn't be present and is an indication that the program struggled to optimize your sequence. Orange corresponds to "problems" which are terminators or strong ribosome binding sites. Red corresponds to "bad problems" which contain an enzyme cut site. Palindromic cut sites are checked on both DNA strands.

<br>

## Algorithm
### Overview
80 attempts are made to generate a sequence from scratch, and if no sequence is perfect (the most likely outcome), the highest-scoring sequence is given 80 attempts to fix the problem areas. Each sequence starts with a score of 100, and every time any imperfection is found, a certain amount is subtracted. It's rather unlikely to get a perfect score, but the reason the score was decreased could be rather minor. **A number is chosen to seed the random processes, so running the same sequence with the same settings will always produce the same result.**
### Codon preferences
The preferences used are ones which indicate how much a given codon is used compared to the other codons which code for the same amino acid. When combining the preferences of multiple species, the end result is generally a weighted average calculated from the specified weights of the species; however, low preferences are calculated differently. When a preference is below 11%, the unweighted average for that codon is found, and the lowest value of the following options is chosen: 1.5 times the lowest species preference, the unweighted average, or the threshold value (11%). Codons with greater preference have their percentages adjusted proportionally to make sure the total continues being 100%. **When only a single species is specified,** all codon preferences are the same as that species except that codons below 8% preference aren't used. The score of a generated sequence is decreased by the floored percent error of the presence of each codon exceeding the tolerance of 100%.
### Avoided sequences
Besides the specified enzyme cut sites, the program tries to avoid the following terminators and ribosome binding sites: aaaaa, ttttt, ggagg, and taaggag. Every appearance of one of those sites penalizes the score by 5 whereas each enzyme cut site penalizes by 10.
### Hairpin checking
For the first 50 nucleotides of the generated sequence, segments of 18, 20, 22, and 24 bases are sampled at every possible location, and the remainder of the 50 nucleotides is checked for the reverse complement of the sample. If a sequence is found that's at least 75% identical (determined by Levenshtein distance), then the melting point of the potential hairpin is estimated (using Wallace's Rule individually on both strands), and if the melting point is determined to be greater than or equal to 60°C, a hairpin is confirmed, and the score is decreased by 5 times the number of hairpins found.
### GC content
Anything above 60% or below 30% penalizes the score by the square of the percentage beyond the threshold. (e.g. GC content of 65% is penalized by 5<sup>2</sup>.)
### Miscellaneous
Capitalization of any sequence doesn't matter. (Everything is converted to lowercase internally.)
