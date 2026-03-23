# Modelling Team Playing Style

Source: https://blogarchive.statsbomb.com/articles/soccer/modelling-team-playing-style

The task of assessing the quality of teams and players has gained much attention in the football analytics space; advanced models such asExpected Goals(xG) andOn-Ball Value(OBV) have become commonplace amongst analysts at all levels of the game. However, much less emphasis has been placed on assessing the stylistic characteristics that teams exhibit. A strong understanding of playing style allows for improved player and manager recruitment by helping to find the most appropriate fit. The evolution of style can also be monitored across periods of time and used to influence tactics based on analysis of upcoming opposition.

As playing style is an inherently subjective concept, there has been no single accepted best modelling approach. Most existing work focuses on creating a style profile through the hand selection of arbitrary rules-based team metrics. From here, a distance metric, clustering methods or classification is often applied. This approach is highly dependent on the subjective task of selecting appropriate metrics and can often lead to certain aspects of a team’s playing style being over- or under- weighted. Also, the metrics chosen for such team playing style models often exhibit a strong team strength bias, leading to the models grouping teams of similar strength rather than similar style. A team’s strength will influence their playing style, but it shouldn’t be the primary factor.

In 2019, the Leuven Group introduced a novel method of profiling the individual style of football players based on previous work done by Franks et al (2015) on NBA players. The work is based on the hypothesis that “playing style manifests itself as where on the pitch a player tends to perform specific actions with the ball”.Their approach encodes the information contained in a player’s event stream data by generating separate heatmaps for open-play in-possession events (passes, dribbles, shots and crosses). This is an intuitive method to display this information in a non-discrete manner. The heatmaps are then compressed using Non-Negative Matrix Factorisation (NMF) which creates meaningful components (characteristics of playing style) from the original heatmaps. This is the key merit of their work as, unlike other approaches, features are not arbitrarily defined - instead, they are generated on our behalf.

However, there are a number of downsides to this approach. Only four event types are used, all of which are in-possession events. Therefore, we do not get a holistic style profile because much of what occurs on the pitch is ignored. We also have the issue of the use of per 90 event frequencies which, as with other methods, introduces a strength bias because stronger players are likely to perform actions more frequently, resulting in their stylistic profiles appearing similar.

The Leuven approach focuses on deriving style from the empirical location of events on the pitch by utilising a combination of heatmaps and NMF. The heatmaps allow us to encode non-discrete locational information while retaining frequency information. NMF enables the model to select the most meaningful characteristics, thus removing subjectivity. When combined, these processes replace the arbitrary metric selection process by automatically defining meaningful features.

We developed upon this high-level approach when building our team playing style model.

We made the following modifications to directly address the shortcomings mentioned above:

We believe that a team’s style of play can be described by the events they perform as well as concede. This includes in-possession event types (passes, carries, shots…) and out-of-possession event types (pressures, tackles, interceptions…). We increased the number of event types for each team's profile from 4 to 32, meaning the model can holistically capture team playing style.

Traditionally, playing style models tend to neglect out-of-possession aspects of team style in favour of the easier-to-quantify in-possession style, mainly because there are fewer out-of-possession event types present in event data. The inclusion of pressure events, the most frequent of all defensive events, goes some way to mitigating the problem by giving us access to a more robust event set - particularly beneficial given the importance of pressing in the modern game.

However, an asymmetry between in-possession and out-of-possession events still remains, which we corrected for by feeding all opposition in-possession events conceded into a team’s out-of-possession profile and all opposition out-of-possession events conceded into a team’s in-possession profile.

When looking at event-type heatmaps, strength bias manifests itself in the frequency and locational distribution of events. Stronger teams perform more in-possession events and fewer out-of-possession events. Similarly, stronger teams perform a disproportionate number of events further up the pitch because their strength advantage allows for easier ball progression.

To suppress this bias, we use the relative frequency of events rather than the raw frequency. For example, looking at the 2021/2022 season, Norwich and Manchester City performed a similar number of aerial passes (4334 and 4494, respectively); however, these made up just 7.6% of Manchester City’s in-possession events compared to 11.2% of Norwich’s in-possession events.

Relative frequency is a more insightful metric as it allows us to model a team’s preferences towards certain event types while reducing the impact of team strength bias. The frequency of in-possession events is found relative to the total number of in-possession events the team performs, and the frequency of out-of-possession events is found relative to the total number of opposition in-possession events conceded.

For a small subset of events (shots, goal kicks, etc), the relative frequency of events still exhibits a strength bias. In such cases, we ignore frequency information and consider solely the locational distribution.

Since the information captured in event locations is fundamental to what constitutes team playing style, we have decided not to control for these distributional differences, so some strength bias is left unaccounted for. We feel this is a worthwhile trade-off given we have already gone some way to suppressing strength bias through the use of relative frequencies.

We made several other modelling decisions to make our team playing style model as accurate, comprehensive, and user-friendly as possible.

We can modify the model to match the desired use case. This includes:

An additional Principal Component Analysis (PCA) layer is applied post-NMF to reduce the influence of highly correlated event types. This is performed separately for the in-possession and out-of-possession profiles to ensure both aspects are considered equally important overall.

The Layered Architecture also lends itself to a highly interpretable model. We can inspect the inputs and outputs at any stage of the process, as we will illustrate below. This can be the qualitative visual assessment of components or the quantitative assessment of the variance explained by the sub-models in each layer.

The locations of all events are mirrored, allowing us to consider events that occur on one side of the pitch equivalent to those in the corresponding location on the other side of the pitch. We do this as we do not want teams with opposite preferences to the right/left flank to be considered completely separate stylistically.

Manager Style is considered to be equivalent to the style we observe their team play. Decoupling manager effect from overall team style is not practical due to the limited sample size. Instead, the stylistic profile of the teams the manager has taken charge of can be monitored over time to analyse their impact on the team’s playing style with a higher degree of nuance. We can also take advantage of the variable time frame to investigate how quickly a manager is able to implement their preferred style or the extent to which they migrate from their style when results do not go their way.

This section demonstrates how NMF is utilised to extract meaningful components from event-type heatmaps.

Aerial Pass Start locations are used as a demonstration. By considering the Aerial Pass Start heatmaps for every team in the training set, the NMF creates components that can be used to represent any team’s original heatmap. That is, when combined in a linear manner, they explain as much of the variance contained in each of the original heatmaps as possible.

The following three components are generated:

We can use these components to recreate any team’s original Aerial Pass Start heatmaps by taking the product of the component and corresponding weights.

Let’s use Burnley 2021/22 as a demonstration.

The reconstructed heatmap closely resembles the original heatmap, shown below. However, the information (variance) previously encoded in a full heatmap can now be described using only the three corresponding weight values (0.418, 0.436, 0.673). For all event types, the average team’s weights sum to 1. Here we see Burnley’s weights sum to 1.527, thus highlighting their preference for aerial passes.

Our model does not explicitly use temporal features when assessing team style. However, we can be confident that this information is captured on both sides of the ball. On the out-of-possession side, the magnitude of heatmaps describes the “aggressiveness” of a team by showing the number of each defensive event performed for every action conceded. This is effectively the reciprocal of passes per defensive action (PPDA) on an event-type basis. However, this has the added benefit of incorporating the locations these events occur.

On the other side of the ball, the magnitude of out-of-possession events conceded provides a proxy for the length of a team’s possession sequences. Further tempo information is captured by a team’s preference towards certain pass types (ground vs aerial) and the location these are performed. When tested, we found that a number of the event type components were highly correlated with tempo-based metrics such as Directness, Pace Towards Goal and PPDA. This indicates that the model can effectively capture team tempo despite not considering it explicitly.

The design of our model allows for expert domain knowledge to be added through the use of additional manually defined events. These have merit in the case of sparse events that represent a small subset of another event type, but are disproportionately important to team style. An example of this is passes into the 18-yard box. Unless manually defined, these events may be considered noise by the NMF; by explicitly defining them, such a risk can be removed.

Below is an example of the components relating to box passes for all Premier League clubs from the 2021/22 season. The left-hand column shows the heatmap components automatically defined by NMF, and the right-hand column shows each team's corresponding weights.

We can see three clear automatically defined components:

The model highlights cutbacks as an important component of how teams move the ball into the box. Although our model generally profiles Liverpool and Manchester City as similar teams in possession, we see a clear contrast between their components for this event type. Manchester City are particularly over-represented in the cutback component, whereas Liverpool are very high on the central component. As expected, Burnley and West Ham are over-represented in the wide crossing component. Plots such as these allow us to analyse how teams pass the ball into the box in a digestible manner. It is more streamlined than the alternative of trying to visually assess the subtle differences in magnitude (colour) across 20 separate heatmaps.

The concept of a playing style is subjective, meaning we have no ‘ground truth’ to compare results against. Ideally, our model will discriminate between teams while also maintaining stability over time.

For this, we will use an evaluation method proposed by the Leuven group to attain a performance statistic. This approach involves randomly separating each team's event into two groups to treat them as separate entities (teams). The similarity rank between each team's two counterparts are used to measure how well the model can match a team against itself purely based on empirical event location distributions and relative frequencies. More specifically, we use the mean of the reciprocals of fractional similarity ranks across all teams, more commonly referred to as Mean Reciprocal Rank (MRR). The metric is scored between 0 and 1, with 1 implying that the model correctly ranks the samples most similar on every occasion.

We tested the model on all teams from the big 5 European leagues and their 2nd tiers from the 2021/22 season. The preferred model attains an average MRR of 0.918, meaning the correct team was ranked first in approximately 90% of cases. While some hyperparameter combinations did yield higher MRR values, we favoured a combination of hyperparameters that yields more interpretable results for its wider range of practical use cases and applications.

To demonstrate how our model can be applied, we will profile Leeds United 2020/21: Marcelo Bielsa’s only full season as a manager in the Premier League and a particularly distinct example of team style.

Below are the five most similar teams in possession, out-of-possession and overall across the big five leagues from the previous two seasons.

Leeds United 2021/22 appear as the most similar team overall, showing that they remained somewhat stylistically stable. This is primarily driven by the high out-of-possession similarity (0.912), second only to Rayo Vallecano 2021/22 (0.913).  Rayo Vallecano provide an interesting example as their in-possession similarity is particularly low (0.4930) compared to Leeds in 2020/21. This shows that the two teams can be similar on one side of the ball but not the other, highlighting the need to decouple these styles.

On the in-possession side, Leeds United 2021/2022 do not feature in the top 5 (ranked 11th with 0.919). One possible explanation is that the managerial changes and injuries Leeds suffered in 2021/22 had a more significant influence on their in-possession style than their out-of-possession style. We also observe that the in-possession similarity scores are generally much higher than the out-of-possession scores, suggesting that Leeds United’s team in 2020/21 was distinctive due to what they did without the ball rather than what they did with it.

All of the top 5 teams for out-of-possession similarity are from La Liga, not a league associated with the same aggressive out-of-possession style Leeds are known for. However, as previously discussed, the architecture of our model allows us to inspect individual heatmap components to explain model outputs. We will perform a small investigation into why these teams are ranked similarly. As a point of reference, we include Liverpool 2021/22 as they’re sometimes considered similarly aggressive in their out-of-possession style to the Leeds 2020/21. However, our model assigns them a similarity score of just 0.599.

We can assess the location and relative frequency at which each team performs pressure events using heatmap component plots below.

The NMF generates three clear automatically defined heatmap components:

From the first component, we observe that - relative to the number of actions Leeds concede - they performed a very high number of pressures close to their own goal across the two seasons, whereas the other teams performed a more moderate number comparatively. In the central areas, we see that Rayo Vallecano perform the highest number of relative pressures, followed by the two seasons of Leeds. The final component shows that the number of pressures performed in the attacking half is very similar across the teams that profiled as stylistically similar. However, Liverpool 2021/22 are considerably over-represented in this component, highlighting the aggressiveness of their press. Summing the weights across these components, we see Leeds 2020/21 come out on top with 1.39 - this is the highest for all teams in the big 5 leagues across the seasons of interest. Liverpool are not dissimilar, with a sum of 1.19 (ranked 10th). Although the number of pressures the teams perform relative to the events they concede is somewhat similar, the distribution of the locations is very different - showing that the two teams are pretty distinct stylistically despite appearing similar at first.

Further research could be undertaken to analyse each of the out-of-possession event types, but hopefully, this goes some way to demonstrating that the modular approach adopted by our model allows us to examine output that may, at first glance, appear unintuitive.

We have developed a new holistic approach to profile team playing style derived from the location and relative frequency of all events that occur on the pitch. Our model addresses a number of shortcomings in existing models, including issues relating to arbitrary feature selection, as well as skewed results due to strength bias. The modular approach allows the user to modify the model in order to suit any use case. Unlike some ‘black box’ models, we are able to inspect the inputs and outputs at any stage of the process. This allows us to understand why the model produces the results that it does, which is vital for decision-making in elite football.