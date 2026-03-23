# Revisiting Pressure With StatsBomb 360

Source: https://blogarchive.statsbomb.com/articles/soccer/revisiting-pressure-with-statsbomb-360

When we first launched StatsBomb Data, we were excited to introduce pressure events, when a player closes down or blocks a passing lane. This was in response to a common complaint about event data, that it only captures what's on the ball - withStatsBomb Datayou're able to find out much more about the defending team's positioning and pressing triggers than with previous datasets. But pressures are a slightly blunt instrument - actions are either under pressure or they're not, there's no grey area in between.

StatsBomb 360gives you a much better window into what a defensive team is doing and where, so today we're going to put our raumdeuter hats on and look at where teams allow or deny raum, and which players are good at deutering it. We can do this because 360 gives you teammate and opponent positions on every single event, and so finding how much space a player has while performing an event is as simple as measuring the radius to the nearest defender, like so:

You don't have to do this yourself though, we'll be adding the distance to the nearest defender (both any defender and the nearest goalside one) in the 360 dataset for the new season. To give some context, let's look at each position in a typical formation so you know how much space they're working with on average:

As you'd expect, the closer to the business end of the pitch, the less space to work in. This isn't a particular revelation, so let's spend some time looking at some specifics about teams and players.

Here are last year's EPL teams plotted by how much space they allow compared to the league average in various zones on the pitch. Picture yourself as the opponent, attacking upwards, with pressure coming from each particular team top to bottom. Red means less space to operate in, blue means more:

There are some interesting highlights here:

This is just a very simple overview of averages, but if you spent time with the 360 you'd quickly be able to start revealing much more detail about team's pressing triggers etc.

As we saw above, closer to an opponent's goal you have less space, but these are the more valuable areas to attack. Let's have a look at the space/value tradeoff and see which players perhaps stand out in the ability to create space in valuable areas or succeed in tight spaces. This chart shows various players, with their position on the X axes showing the average space in which they receive passes, and the Y axis showing the averageOBVvalue for their team upon receipt:

As you can see, the relationship is mostly linear - defending teams pressure the ball in direct relation to how dangerous a situation is. But it's interesting to spot a few players riding high or low above the line:

However, just a raw plot of these values doesn't tell us very much. We're much more interested in specifically where players are operating with the ball, and whether they manage to find additional space in those values. If we could build a model to measure this, we might be able to start valuing a player's off-ball movement, in a way that's impossible with current event data.

To do this, I built a model called Space eXpected, or XSpace for short. Let's see if it blows up on the launchpad.

The model is a pretty simple gradient boosted trees approach that takes in some simple features like the type of action, where on the pitch an action takes place, some player positional info, the current OBV situation and the identity of the opposition, because different teams allow different amounts of space in various zones. We train this on passes, carries, receipts and shots. In the ideal world the model would also take into account your own team's ability to create space, so we could measure that independent to individual players, but this will do for now.

We can then compare the XSpace of each action with the actual distance to the nearest defender. I use a simple ratio of real space to expected space to measure Space Above Expected, or SAX. Who are the best SAX players?

Here's the list of the best creators (wingers, AMs etc, excluding strikers):

Sterling stands out here like before, but he's beaten out by new Barcelona man Raphinha (so good at finding space he can even find room in Barcelona's budget). Leeds' other winger Jack Harrison also makes the top 10, clearly highlighting some team effects here. Also near the top is 20-year-old Michael Olise at Crystal Palace, who has been cashing in well on the space he's given, as he also appears in the top 10 for assists per 90 last season. Olise has been subject to rumours about a move to Newcastle in recent weeks.

We can visualise where these players are finding room in the space map below, each circle representing an action and the distance to the nearest defender, which brighter red being more space above expected and more transparent blues being less:

Yes, after two years of pandemic this looks a little like something untoward growing in a petri dish but garish shapes are my bread and butter. Hopefully there's enough signal to noise here:

Sad to see Robertson here and not Alexander-Arnold, but this isn't to say TAA isn't creating value. In fact if anything, he's such a known quantity in attack that he probably draws a lot of pressure, and perhaps this benefits his teammate on the other wing. Either way, Robertson is clearly excellent up and down the length of the pitch. Tsimikas deputises ably, but you can see a clear difference in magnitude between the two.

It's important to note that whatever you think of the results here, and of xSpace and SAX themselves, they areonlypossible because of the existence of StatsBomb 360. There's a huge wealth of knowledge waiting to be unearthed in the dataset, as already shown inJames Yorke's recent piece about line-breaking passes, and we've got much more to come as we delve deeper and ship new data to our existing 360 customers.