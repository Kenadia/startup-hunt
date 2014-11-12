Startup Hunt
=

by Ken Schiller

```
usage: main.py [-h] [candidate_json]
```

This script takes a candidate profile, in JSON, as input, and returns a list of companies relevant for the candidate to apply to. A JSON file can be provided as the first argument, otherwise JSON will be read from standard input.

The following keys are recognized and used as follows:

**resume**: Path to a local or online PDF file. If any company names are found, then startups in related markets will be added to the list of potential matches.

**locationPreferences**: A list of locations. Companies in the same locations will be added to the list of potential matches.

**marketPreferences**: A list of markets. Companies in the same or related markets will be added to the list of potential matches.

The top ten companies out of all potential matches are determined by the following rating system: 5 points for each match (a company can match multiple times according to the candidate data) and 1 point for each point of “quality” out of 10 as rated by AngelList.

Examples
-

**examples/example1.json**: The startups at the very top of the returned list are those with both a location and market listed among the candidate's preferences. Soon after are some startups that only matched either location or market, but that had a high “quality” rating.

**examples/example2.json**: This is an example of using an online PDF to source information about a candidate. In this case, my resume is used. Indiegogo is found, and companies in similar markets (Finance) are returned.

**examples/example2.json**: Same as the second example, but using a local file.
