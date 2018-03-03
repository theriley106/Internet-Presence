# Awareness
Giving consumers knowledge about the data they're giving away...

### Useful links

https://developers.facebook.com/docs/marketing-apis

### Facebook

Email addresses - Use key EMAIL. Trimming leading and trailing whitespace and convert all characters to lowercase.

Phone numbers - Use key PHONE. Remove symbols, letters, and any leading zeroes. You should prefix the country code if COUNTRY field is not specified.

Gender - Use key GEN. m for male and f for female.

Birth Year - Use key DOBY. YYYY from 1900 to current year.

Birth Month - Key DOBM. MM format: 01 to 12.

Birthday - Key DOBD, DD format: 01 to 31.

Last and first names - Keys LN and FN. a-z only. Lower case only, no punctuation. Special characters in UTF8 format.

First Initial - FI, first character of normalized first name.

US States - ST in 2-character ANSI abbreviation code, lower case.

Normalize states outside U.S. in lower case, no punctuations, no special characters, no white space.

City - CT as a-z only. Lower case, no punctuations, no special characters, no white space.

Zip code - ZIP. In lower case, no white spaces. Use only the first 5 digits for U.S. Use Area/District/Sector format for UK.

Country code - COUNTRY. 2-letter country codes in ISO 3166-1 alpha-2.

Mobile advertiser id - MADID, all lower case. Keep hyphens.
