sample_content = """
TITLE: Paper Summary: What Makes Rope Useful
Oct 23, 2024 · 922 words · 5 minute read
Table of Contents
1. RoPE does not necessarily decay activations with distance:
2. Not all frequencies are the same, lower frequencies are not important for positional information, only semantic:
3. Low frequencies can be removed entirely
4. Implication of extrapolation and training
Conclusion
Up until now everyone has been using “Rotary Position Embedding” (RoPE) like a default method for positional encoding for awhile. However, specifically how and why RoPE makes things “better” is still a little unexlored.

Luckily there is a paper Round and Round We Go! What makes Rotary Positional Encodings useful? addressing this specific issue. I found a few of their results are quite interesting.

1. RoPE does not necessarily decay activations with distance: 
In the original paper RoFormer the authors made an analysis about the fact that RoPE has some level of decay of the increasing of the context len. However, the new paper we are discussing here argued that this is not actually an practical analysis. Let’s take a look at the below result.

RoFormer

As you can see on the left is the result from the original paper with constant queries and keys, which having the value of “1”. The interesting thing is that this might not be a practical assumption. In practice, queries and keys are never having values of 1, but most likely having some sort of randomized distribution.

To challenge this analysis, the authors in the new paper re-test the idea with Gaussian queries and keys. As can be seen from the second chart, it is very obvious that there is no visible decay with Gaussian queries and keys. On a practical note, this also is closer to what we might see in real scenario.

Since there is no visible decay in attention when using RoPE over a long context length, this might contribute a bit to the fact that most of the current models using RoPE have significantly long context windows.

2. Not all frequencies are the same, lower frequencies are not important for positional information, only semantic: 
As you might have known a “rotated” embedding does not simply just use one angle, but a range of them (if not please visit my old blog post). Specifically following this formula.

G
=
g
k
=
θ
−
2
(
k
−
1
)
d
for
k
=
1
,
…
,
d
2
G=g 
k
​
 =θ 
− 
d
2(k−1)
​
 
 fork=1,…, 
2
d
​
 

Where k is just position of the complex number pair, d is basically dim of embedding.

Ideally because there are so many frequencies that are being used here (based on so many angles) for just one single embedding, it is pretty straightforward to think not all the frequencies are being used in the same way.

From the paper, it is observed as such.

LowFreq

As per observed from the paper frequencies usage and activities vary significantly because low and high frequencies. In this case you can see the low frequencies are made use more in the charts.

More interesting results:

The usage of low frequencies is not for “positional” and mostly contain semantic (inherently knowledge) information, there are some math involved in proving this in the paper
High frequencies on the other hand, containing positional information and very few semantic information (information about which phrase come first and last)
3. Low frequencies can be removed entirely 
The above result combined with some observations in practice:

Llama3.1 model seems to perform well on very high base wavelength (theta) on long context length.
Semantic bands are not robust over long contexts.
If base wavelength is high, the low frequencies are very low, and this will make the change in the value of the queries and keys almost negligible.
Example: If increase the angle to 60 to 61 by multiply a complex number with angle 60 to a complex number having angle of 1, the projected value is very small.

LowFreq

Well! In practice the number is much smaller due to the base frequency is extremely high (you can check llama3.1 and gemma model). Because the value of the base frequency are so high, the impact of the frequencies to actual queries and keys values are also very small.

With the above observations, in the paper the author has tested removing lower frequencies entirely and only keep higher frequencies by introducing a new method to do Rope.

The paper introduce p-Rope which essentially is a way to do rope which control on which frequencies are excluded. In this case if excluding the lower frequencies, models are showing the same performance. This might be due to the fact that the low frequencies contain only semantic information.

4. Implication of extrapolation and training 
This part I also make some deductions, but we can see a few things.

Llama3.1 has shown very robust ability to extrapolate to very long context length beyond the training set (per their paper and technical report)
The model can apply its understanding of short data to longer contexts. In other words, you don’t need the same amount or quality of data for longer context windows to get high performance. The model can still perform well on longer inputs by using the semantics from the shorter data it was trained on.
Control the usage of frequencies in LLM model can increase the model performance on longer/shorter context length significantly.
Conclusion 
I hope this summary has given you a deeper understanding of what makes RoPE so useful, especially in the context of large language models. The paper challenges some older assumptions, showing that RoPE maintains its effectiveness over long contexts and how different frequency bands serve unique roles—low frequencies carrying semantic meaning and high frequencies capturing positional data.

With innovations like p-RoPE, which streamlines the process by excluding lower frequencies, there are exciting opportunities to improve model performance without sacrificing efficiency. I hope you’ve learned something new, and that these insights spark more curiosity about the intricacies of AI!

ai
"""

sample_guide_prompt = """
rewrite my blog post in a readable format. remove markdown. convert complicated symbol and math symbol into plain words. The writing should be suitable for reading out loud and doesn't contain things like headers, indentation, list form etc.... and should be just a verbally readable text. cut long paragraph into many smaller paragraph if possible.

Must be really simple and easy to read out loud. Below are the example of the perfect output:
Example:
Today, we’re discussing a fascinating paper titled “Round and Round We Go! What Makes Rotary Positional Encodings Useful?” It dives into why Rotary Positional Embeddings, or RoPE, have been so effective in large language models and even challenges some of the early assumptions about how they work.

Let’s start with the first big idea. For a while, people believed that RoPE causes activations to decay as the context length increases. This idea came from the original RoFormer paper, where they showed that when queries and keys were held constant at a value of one, the attention scores seemed to drop off with distance.

But here’s the catch—queries and keys aren’t constant in real-world scenarios. They vary randomly. A newer study tested this with more realistic settings, using Gaussian distributions for queries and keys instead of fixed values. And guess what? They didn’t find any significant decay in attention scores, even for longer distances. So, this means RoPE holds up really well in models that work with long context windows.

Now, moving on to frequencies. RoPE works by combining different frequencies from a range of angles, and these frequencies do very different things. High frequencies focus on structure—they’re all about capturing where words are in relation to each other.

Low frequencies, on the other hand, carry more semantic information. It’s like the high frequencies handle the framework of a sentence, while the low frequencies add meaning to the content.

Here’s where things get even more interesting. Researchers found that you can actually remove the low frequencies without much impact on performance. By using higher base wavelengths, which reduce the importance of low frequencies, models like Llama3.1 still performed really well.

Why? Because the semantics carried by those low frequencies were already being handled elsewhere in the model. Removing them made the system more efficient while keeping the results just as good.

To take this further, the paper introduced something called p-RoPE. This method lets you selectively exclude certain frequency bands and focus only on the high frequencies. The result? Models that are not only efficient but also capable of maintaining strong performance across both short and long sequences.

Finally, let’s talk about what this means for training. These findings show that models trained on shorter sequences can still handle much longer ones. That’s because they don’t rely entirely on positional data—they also use semantic information.

This could mean less training data is needed for long-context models, making them more scalable. And by fine-tuning which frequencies RoPE emphasizes, researchers can optimize performance for different tasks.

In summary, this paper flips some of our earlier assumptions about RoPE. It shows that the embeddings stay effective over long context lengths and explains how different frequency bands play unique roles. High frequencies capture structure, low frequencies add meaning, and innovations like p-RoPE let us fine-tune these components for better efficiency and adaptability.
---------
Now please do the same with the below post
"""
