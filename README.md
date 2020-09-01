# Auto Filler for UTD's Daily Health Check
This program automatically fills out the survey sent by UTD every day asking about your health.
It is comprised of a simple email bot that waits for an email that includes the link
to your survey, and uses a Selenium script to fill it out depending on whether you
are on or off campus. The script is running 24/7 on my machine so you can make use of it.

To use this, you can forward your emails from `redcap@utdallas.edu` to
`YesOnCampus@gmail.com` or `NoOnCampus@gmail.com`, depending on your answer to the first
question, and the bot will automatically fill out all options for a healthy student<sup>[1]</sup>.


You can also set up automatic forwarding by adding a rule on Outlook:
1. Navigate to your UTD email on outlook.
2. Select an email from `redcap@utdallas.edu` and click the 3 dots (...) for more actions
3. In the menu select `Advanced Actions > Create Rule`
4. In the new window click `More options`
5. In the drop down for `Add an action`, select `Forward to`
6. In the field add either `YesOnCampus@gmail.com` or `NoOnCampus@gmail.com` for
whatever answer you usually choose.
7. That's it! No more manually filling out the survey.

**<sup>[1]</sup> IF YOU ARE NOT A HEALTHY STUDENT AND SHOW SYMPTOMS OF COVID-19, MAKE SURE YOU TAKE CORRECT ACTION.
THIS INCLUDES DISABLING AUTO FORWARDING AND FILLING OUT THE SURVEY TRUTHFULLY AS SOON AS POSSIBLE.**