## [https://devpost.com/software/awareness](View the Project on DevPost)

### Inspiration

The widespread exposure of personal information on the internet. We want to bring awareness to the community of how much personal information is out there on the internet.

### What it does

It allows users to search their name and location, or scan their barcode, to find if there is any personal information online. It gathers information from various social media sites such as Facebook and LinkedIn, and checks sites containing public information.

### Supported Bar Code Types:

 -UPC-A and UPC-E

- EAN-8 and EAN-13

- Code 39

- Code 93

- Code 128

- ITF

- Codabar

- RSS-14 (all variants)

- RSS Expanded (most variants)

- QR Code

- Data Matrix

- Aztec ('beta' quality)

- PDF 417 ('alpha' quality)

- MaxiCode

### How we built it

Using Flask framework as the back end, and Bootstrap in the front end. Used REST API, Selenium to bypass scraping limits, and ZXing.

### Challenges we ran into

We intended it to be a mobile app and have more elaborate functions. The learning curve for Swift was very high especially when we didn't have any experience working with it. Formatting the UI via HTML and CSS.

### Accomplishments that we're proud of

Integrating the technology that allows scanning of barcodes with personal information, and searches this information in the internet. We are proud of the accessibility features we provided. Being able to scan your I.D. empowers people who don't have the ability to type or have full access to technology. First open-source Flask-based Barcode scanner that supports PDF417.

**The technology does not release any personal information from the user's entry or their driver's license.**

### What we learned
The vast amount of resources available online that can be used to search your personal information. How much information one can obtain about a person using just their name, and location.

### What's next for Internet Presence

- Include more sources for obtaining data on a person. Eventually we would leverage this information to incentivize users to reduce their internet presence by being aware of their privacy settings and which applications share your personal information.

- A share button that allows a user to share with their friends what kind of information they found out about themselves. This will allow people to become more aware of the widespread data that's out there on the internet.
