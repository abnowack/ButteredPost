. - any character
    c.t = cat, cot, cct, ...
\ - escape, turn operators into literals
    c\.t = 'c.t'
[] - like ., but for multiple characters at once
    c[abc]t = cat, cbt, cct
    
    Shortcuts
    [A-Z] = [ABCD..Z]
    [0-9] = [0123..9]
    [A-Z0-9] = [ABCD..Z0123..9]  You can combine these shortcuts
    
    *Note, hypens are literals except when in []
    
    [^a] = any character NOT a
    [^A-Z] = any character NOT ABCD..Z
    [^a-zA-Z0-9] = any nonalphanumeric character
    
    And there are even shortcuts for these shortcuts
    
    [\d] = [0-9]
    [\w] = [0-9A-Za-z]
    [\s] = Find a whitespace character
    Also the opposites ^
    \D = ^\d
    \W = ^\w
    \S = ^\s
    
{#} - Multiplier, turns a{5} into aaaaa

    Can have ranges, a{3,5} will match aaa, aaaa, aaaaa
    Can be open ended, a{3,} will match aaaaaaaaa too
    
    Shotcuts:
    ? = {0,1}
    * = {0,} which is just find anything
    + = {1,}
    
    By appending a ? to the end of a multiplier, the preference is to find the smallest match first
    So ".*?" will look for the shortest fragment surrounded in double quotes
    "this is a "nested" quote" returns "this is a " using ".*?" while ".*" returns the entire thing
    
| - Alternation, an OR statement

    cat|dog = find cat or dog
    a|b = [ab]
    [ab|cd] = Find 

() - Group expressions, can apply operations on them
    (Mon|Tues|Wed|Thurs|Fri)day = match a weekday
    \w+(\W\w+){3} = Find four words

\b - Word boundary,
    `example` `here` `it`'`s` `great`
    \b would match each ` mark, which symbolizes a word boundary

^ - Start of a line
$ - End of a line

    ^.*$ will match entire text, ^.*?$ will match smallest line

() - Also capture groups, capture will return all matches in the ()

