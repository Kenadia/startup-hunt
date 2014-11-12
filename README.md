Startup Hunt
=

by Ken Schiller

This script takes a candidate profile, in JSON, as input, and returns a list of companies relevant for the candidate to apply to.

The following keys are recognized and used as follows:

**resume**: Path to a local or online PDF file. If any company names are found, then startups in related markets will be added to the list of potential matches.

**locationPreferences**: A list of locations. Companies in the same locations will be added to the list of potential matches.

**marketPreferences**: A list of markets. Companies in the same or related markets will be added to the list of potential matches.

The top ten companies out of all potential matches are determined by the following rating system: 5 points for each match (a company can match multiple times according to the candidate data) and 1 point for each point of “quality” out of 10 as rated by AngelList.
