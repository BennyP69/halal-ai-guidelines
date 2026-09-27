# Checked rulings library

Only records whose source was actually opened and read. Each says what was and was not
checked. A record covers ONLY the case it describes; different facts need a new check.

Record format for new entries:

```
### <short topic>
- Question: <exact case the scholar was asked>
- Authority: <scholar> | Source: <url> (+ book/vol/page if given)
- Checked: <what was read: Arabic original / translation only / audio not checked>
- Words: «verified Arabic excerpt» - <labeled translation>
- Ruling: <one line, attributed>
- Conditions: <when it applies / exceptions>
- Evidence cited by the source: <verses/hadith as the source gives them; "not given" if absent>
- Gap: <how a modern case may differ>
- Added: <date>, verified by halal.py verify: yes/no
```

---

### Passing on a scholar's ruling
- Question: Someone repeats a fatwa they heard on the radio program Nur 'ala al-Darb.
- Authority: Ibn Baz | Source: https://binbaz.org.sa/fatwas/10976/
- Checked: Arabic question and answer on the official archive. Audio not checked.
- Words: «تنسبه إلى صاحبه» - "attribute it to its owner" (my translation)
- Ruling: Allowed to pass on a ruling accurately, attributed to the scholar, when it was
  reliably remembered; not when uncertain or altered.
- Gap: Supports careful quoting. Does not let software make new rulings.
- Added: 2026-09-12

### Working in a bank that deals in riba
- Question: Working in banks, and depositing money in them.
- Authority: Ibn Baz | Source: https://binbaz.org.sa/fatwas/19005/ (cites Majmu' Fatawa wa
  Maqalat 19/415; Fatawa Islamiyyah 2/397)
- Checked: Arabic on the official archive. Printed editions not compared.
- Words: «لأن ذلك إعانة لهم على الإثم والعدوان» - "because that is helping them in sin and
  aggression" (my translation)
- Ruling: Not allowed to work in banks that deal in riba, because it helps them in wrongdoing.
- Evidence cited by the source: Qur'an 5:2; Sahih Muslim 1598 (curse on all parties to riba).
- Gap: About bank employment. Not a direct answer on every outside supplier to a bank.
- Added: 2026-09-12

### Working at a company that has some interest dealings
- Question: Working for a company that deals with interest-based banks.
- Authority: Ibn Baz | Source: https://binbaz.org.sa/fatwas/5400/
- Checked: Full Arabic on the official archive. Audio not checked.
- Words: «لكن كونه يعمل الربا بنفسه أو يساعد عليه» - "but for him to do riba himself or help
  with it" (my translation). Verified by halal.py verify on 2026-09-19.
- Ruling: Working there is not forbidden in the case described, because the haram part is
  small relative to its business; doing or helping with the riba yourself is forbidden;
  leaving it for cleaner work is more cautious.
- Evidence cited by the source: "Leave what makes you doubt for what does not" and "whoever
  avoids doubtful things protects his religion" (hadith; collection numbers not given on page).
- Gap: Read together with the bank ruling above. The worker's actual role decides it.
- Added: 2026-09-12

### Earnings from a haram activity
- Question: When Allah forbids something, are its earnings forbidden?
- Authority: Ibn Uthaymeen | Source: https://www.troid.org/when-allah-prohibits-something-its-earnings-are-also-prohibited/
  (Ta'liq 'ala al-Siyasah al-Shar'iyyah, pp. 163-164; trans. Munib al-Sumali)
- Checked: Site translation only. Arabic book not checked. Hadith grading not traced.
- Ruling: Earnings from a forbidden activity are forbidden, across contract types (example
  given: renting a shop for beard shaving).
- Gap: Do not stretch the example to every shop or mixed business without checking.
- Added: 2026-09-12

### Late fee / penalty for delayed installment payment
- Question: Selling an item to be repaid at a specified later date - is it permissible to
  stipulate a conditional penalty, so if the person is late to pay, the repayment amount
  is increased?
- Authority: Salih Al-Fawzan | Source: https://abukhadeejah.com/shaikh-salih-al-fawzan-the-ruling-on-late-fees-fines-penalties/
  (trans. Abdullah Abdul-Wahid Alam, v1.0 02 Aug 2023; original video embedded on page)
- Checked: Site translation in full. Arabic original not checked (video only, captions
  not verified).
- Words: "This is the Riba (usury) of Jahiliyyah (pre-Islamic ignorance) and it is not
  permitted" (site translation). Verified by halal.py verify on 2026-09-19.
- Ruling: Al-Fawzan: a late fee that increases the debt because payment is delayed is the
  riba of Jahiliyyah ("pay now or pay more") and is forbidden for both parties to agree to.
- Conditions: What IS allowed per the same page: setting a higher price at contract time
  for deferred payment, or a discount for early/upfront payment - agreed before the sale,
  never added later for delay ("it is allowed for him to sell for a higher price if his
  payment is to be delayed", verified same date). Supporting: Abu Khadeejah's mortgages
  article, "It is not allowed to charge a late fee if the instalment is paid late because
  that is clear riba" - even if the fee is given to charity - citing Al-Majma' al-Fiqh
  al-Islami, 6th gathering, Jeddah 1410AH/1990CE
  (https://abukhadeejah.com/islamic-mortgages-shariah-compliant-murabah-ijarah-musharakah-riba-instalments/,
  verified same date). Related principle: Ibn Baz https://binbaz.org.sa/fatwas/7166/ (Arabic
  read in full): money paid in exchange for extending a debt's time is riba even if called
  a gift.
- Evidence cited by the source: Qur'an 2:280 referenced in the mortgages article (grant
  the debtor in hardship more time); hadith numbers not given on the Fawzan page.
- Gap: Fawzan's case is a sale/debt installment. A coaching payment plan is installments
  on an agreed service price - same structure (fixed debt, extra charge for delay). Service
  suspension for non-payment was not addressed by these sources.
- Added: 2026-09-19, verified by halal.py verify: yes

### Bank credit card paid off before interest is charged
- Question: Bank cards where bills are charged to the account; if the balance does not cover
  them, the bank charges interest at set rates. Ruling, and what to do if it happened before?
- Authority: Ibn Uthaymeen | Source: https://binothaimeen.net/content/2433
- Checked: Full Arabic Q&A. Page renders via JavaScript, so text was pulled from the site's
  own API (shekhapi.binothaimeen.net/lessons/audios/show/d99247cf-9872-44ed-a6e4-d2c6e9ca85da/0/1)
  and each quote confirmed present in that official response. Audio not checked.
- Words: «هذه المعاملة حرام؛ لأنها معاملة على التزام الربا، وهو إن كان يدفع قبل أن يحل عليه
  الربا، لكنه قد دخل على التزام الربا، فهي حرام» - "This transaction is haram, because it is a
  transaction upon a commitment to riba. Even if he pays before the riba falls due, he has
  entered upon a commitment to riba, so it is haram." (my translation)
- Ruling: Ibn Uthaymeen: the credit card contract is haram even for someone who always pays
  before interest is charged, because signing it is itself agreeing to riba.
- Conditions: Applies to cards whose contract charges interest on late payment. Past use where
  the person gained a riba surplus: give that surplus away in charity to be rid of it; if the
  bank wrongly took interest FROM him, repentance suffices, he was the wronged one.
- Evidence cited by the source: not given on the page beyond the riba reasoning.
- Gap: He was asked about interest-charging bank cards. A card contract with no interest
  clause at all was not this question; see the withdrawal-card record below.
- Added: 2026-09-19, verified programmatically against the official API: yes (3/3 quotes FOUND)

### Same case, second answer: Visa card paid within the free period
- Question: Banks issue a (Visa) card; you take an amount and repay the same amount within
  45-50 days, no interest taken. Ruling?
- Authority: Ibn Uthaymeen | Source: https://binothaimeen.net/content/4151 (same API method as
  above, item 45bd7935-037b-414a-8230-605b8574a4db)
- Checked: Full Arabic Q&A via the official API; quotes confirmed present. Audio not checked.
- Words: «فأصل دخوله على مبدأ الربا حرام» - "so the very act of entering upon the principle of
  riba is haram" (my translation); also «وهذا حرام لا يجوز» - "this is haram, not permissible".
- Ruling: Ibn Uthaymeen: haram even if the person is confident he will pay in time, and even
  if he is rich and certain to pay; circumstances can change, and the entry itself is the problem.
- Added: 2026-09-19, verified programmatically against the official API: yes (3/3 quotes FOUND)

### Plain withdrawal (debit) card with no riba clause
- Question: The withdrawal card called (Visa) used when traveling to withdraw one's own money
  abroad instead of carrying cash. Ruling on withdrawing with it?
- Authority: Ibn Uthaymeen | Source: binothaimeen.net official API item
  e36b5411-ee1f-4da8-a058-450486ac00f3 (site page is JS-rendered; likely content/3508)
- Checked: Full Arabic Q&A via the official API; quotes confirmed present. Audio not checked.
- Words: «لا بأس للإنسان أن يستعمل الفيزة» - "there is no harm in a person using the Visa"
  (my translation); «الأصل في جميع المعاملات الحل والإباحة» - "the default in all dealings is
  permissibility" (my translation)
- Ruling: Ibn Uthaymeen: using such a card to access your own money is fine; dealings are
  allowed unless proof forbids them.
- Gap: This is a card with no riba commitment (own funds). Do not stretch it to credit cards
  with interest clauses; those fall under the two records above.
- Added: 2026-09-19, verified programmatically against the official API: yes (2/2 quotes FOUND)

### Third party pays the seller, buyer repays the financier with increase (BNPL structure)
- Question: A bank gives a person the price of a farm machine so he can take it from a
  company, and he repays the bank in installments over three years with a known increase
  over the current price - is this riba or a deferred sale?
- Authority: Ibn Baz | Source: https://binbaz.org.sa/fatwas/12835/
- Checked: Full Arabic Q&A on the official archive. Audio not checked.
- Words: «هذا يعتبر من الربا» - "this is considered riba" (my translation); «ما يجوز هذه
  الزيادة ربا، ولا يكون بيعًا، هذا قرض» - "this increase is not allowed, it is riba; it is
  not a sale, it is a loan" (my translation)
- Ruling: Ibn Baz: a financier paying the item's price for the buyer, to be repaid with an
  increase, is riba - an interest loan, not a sale. Not permissible.
- Conditions: Allowed alternative on the same page: the company itself buys the item, takes
  real possession, then sells it to the buyer at a known installment price («ثم باعها عليه
  بآجال وأقساط معلومة فلا حرج», verified).
- Evidence cited by the source: the Prophet's prohibition «لا تبع ما ليس عندك» (do not sell
  what you do not have); collection numbers not given on the page.
- Gap: He was asked about agricultural banks. BNPL providers (Klarna, Tabby, Tamara,
  similar) match the forbidden form when repayment exceeds the price (interest plans), and
  their no-interest plans still carry late-fee clauses (see late-fee record above and Ibn
  Uthaymeen credit-card records: entering a riba commitment is itself haram). The
  merchant-side question - offering such a provider at your checkout - was not directly
  asked in any source found; nearest is the helping-riba record (binbaz 19005).
- Added: 2026-09-19, verified by halal.py verify: yes (3/3 quotes FOUND)

### Pay-to-enter prize draw / lottery (yanasib)
- Question: (a) Lottery operations organized by charitable bodies to fund education, medical
  care, and social services - allowed? (b) The lottery found outside this country - ruling?
- Authority: Ibn Baz | Sources: https://binbaz.org.sa/fatwas/17536/ (cites Fatawa Islamiyyah
  vol 4 p 442; Majmu' Fatawa 19/58) and https://binbaz.org.sa/fatwas/25404/
- Checked: Full Arabic Q&A on the official archive for both. Audio not checked.
- Words: «عنوان لعب القمار» + «وهو الميسر، وهو محرم بالكتاب والسنة والإجماع» - "the very name
  of playing qimar (gambling) ... it is maysir, forbidden by the Book, the Sunnah, and
  consensus" (my translation). Second fatwa: «هذا قمار» - "this is gambling" (my translation).
- Ruling: Ibn Baz: the lottery (pay money, chance draw decides who wins a prize) is qimar/
  maysir, haram by Qur'an, Sunnah, and consensus.
- Conditions: Haram even when proceeds go to charity: «سواء كان ذلك المال الذي يحصل بالقمار
  يصرف في جهات بر أو في غير ذلك» - "whether that gambling money is spent on charitable causes
  or otherwise" (my translation). Winnings are forbidden earnings.
- Evidence cited by the source: Qur'an 5:90-91.
- Gap: A prize draw with NO payment to enter was not this question; needs its own check.
- Added: 2026-09-19, verified by halal.py verify: yes (4/4 quotes FOUND)

### Worldly dealings are allowed unless proven otherwise
- Question: The default ruling for ordinary (non-worship) activities.
- Authority: Ibn Taymiyyah (quoted by TROID; not one of the 11, cited by them widely) |
  Source: https://www.troid.org/the-principle-of-permissibility/ (Al-Qawa'id al-Nuraniyyah,
  pp. 112-113)
- Checked: Full translated article. Arabic not checked.
- Ruling: Worship needs a proof to be done; worldly dealings need a proof to be forbidden.
- Evidence cited by the source: Qur'an 42:21, 10:59.
- Gap: Stops invented bans. Does not make a specific unclear deal automatically fine.
- Added: 2026-09-12
