---
title: 'The Hays Discount, Five Years Later'
date: 2026-04-21
permalink: /posts/2026/04/hays-discount/
related: false
tags:
  - Hays County
  - Texas
  - housing
  - public finance
---

Two weeks ago I put a single number at the center of [the Hays County growth
post][growth]: $135,000. That was the gap, in February 2026, between the
median home in Travis County and the median home in Hays County — the
rough math a family is doing when they pull off the highway in Buda or
Kyle instead of continuing north to Austin.

A reader emailed to ask the obvious follow-up. Has it always been
$135,000? Is the gap closing? Widening? Holding steady? If Hays County's
whole growth story runs on an affordability arbitrage, the shape of that
arbitrage over time is worth understanding.

So I pulled Zillow's Home Value Index monthly for Travis, Williamson, and
Hays counties from January 2020 through the latest release, and paired
it with Freddie Mac's 30-year fixed rate from FRED. Five years, one
pandemic boom, one rate shock, and one partial correction. Here is what
the gap actually did.

## Everyone Rode the Same Wave

The first thing to notice is that these three counties move together.
All three rose sharply in 2021 and early 2022, peaked inside a couple of
months of each other in mid-2022, and have been grinding lower since.
Travis stays on top, Williamson in the middle, Hays at the bottom — the
ordering that makes the growth story work never breaks.

![Central Texas home values, 2020 to 2026](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_levels.png)

The commute sheds didn't decouple during the pandemic. They boomed
together and corrected together. That matters, because it rules out the
simplest version of "Hays is getting left behind" — the Hays curve looks
like the Travis curve with a lower intercept.

## The Dollar Gap Bulged, Then Pulled Back

Now subtract. The absolute dollar gap between Travis and Hays was about
$100K at the start of 2020. It peaked at roughly $175K in July 2022. It
sits at $135K today.

![The dollar gap over Hays, 2020 to 2026](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_absolute.png)

That swing is not small. Measured on this axis, the 2022 Travis home was
$40,000 more out of reach than the 2026 Travis home is — a real, if
uneven, narrowing of the absolute spread. If the story ended here you
could argue that Hays's relative advantage has shrunk in Austin's
post-boom cooling and that the migration pipeline should be easing.

It doesn't end here.

## The Premium Is the Invariant

Divide instead of subtract, and the picture changes. Travis's median
home has been, almost continuously, about 138 percent of Hays's. The
mean premium over the full window is 37.4 percent, with a standard
deviation of 0.9 percentage points. That is not a trend. That is a flat
line with noise.

![The percentage premium over Hays has barely moved](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_relative.png)

Williamson's premium over Hays has drifted up by a few points over the
five years, from around 12 percent to 15 percent. Travis's has not
moved. Whatever forces set the price of a house in Travis relative to
the price of a house in Hays — commute time, school district, water
rights, amenities, perception — they did not loosen during the boom and
they did not tighten during the correction. The ratio is sticky in a
way the absolute gap is not.

## Rates Did the Work

Here is the twist. The absolute dollar gap narrowed by $40K between
mid-2022 and today. Over the same period, the 30-year fixed rate
climbed from roughly 3 percent to roughly 7 percent. Principal and
interest on a 30-year loan for that gap looked like this:

![What the gap costs each month](https://raw.githubusercontent.com/scottlangford2/scott_langford/master/images/hays-discount/gap_payment.png)

In 2020, financing the $100K Travis-over-Hays gap at 3 percent meant
about $420 a month in principal and interest. Today, financing the
$135K gap at 7 percent means about $890. The absolute gap got smaller.
The monthly gap more than doubled.

For a family deciding whether to buy in Travis or Hays, the monthly
payment is the binding constraint. On that measure, Hays is more
discounted than it has ever been, not less. The affordability
arbitrage that drove the 2010s wave south has, if anything, sharpened.

## So What Does This Mean for the Migration Pipeline?

The [projections post][projections] treated migration as a scalar —
half of the 2010s rate, full rate, zero. What these five years of
prices suggest is that the relevant migration forcing function is
roughly constant. The percentage premium on Travis has barely moved.
The monthly cost of that premium is higher now than it was during the
boom. None of the price signal says the southward flow should slow.

What it does not tell you is whether the people who *can* afford the
payment are still willing to make the commute, or whether they prefer
to rent, stay put, or go further out to Bastrop or Caldwell. Price is
the pressure; it isn't the flow. That's for another post.

---

## Sources

Zillow Home Value Index, all homes, middle tier, smoothed and
seasonally adjusted, monthly, county level. Freddie Mac Primary
Mortgage Market Survey 30-year fixed rate, weekly, via FRED series
`MORTGAGE30US`.

Replication code: [southbound-35/posts/affordability-gap][repl].

[growth]: {{ site.baseurl }}/posts/2026/04/hays-county-growth/
[projections]: {{ site.baseurl }}/posts/2026/04/hays-county-projections/
[repl]: https://github.com/scottlangford2/southbound-35/tree/main/posts/affordability-gap

## Disclosure

This blog post was written with the assistance of Claude (Anthropic).
Claude helped with data research and drafting. All analysis and
editorial judgment are the author's.
