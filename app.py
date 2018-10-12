from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import re
# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    words = TextField(validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
    filename = "lexicon.txt"
    print(form.errors)
    if request.method == 'POST':
        words=request.form['words'].lower() #to match the case of the dictionary
        misspelledWords = []

        if form.validate():
            # Save the comment here.
            wordsList = words.split(' ')
            for w in range(len(wordsList)):
                wordsList[w] = re.sub(r'\W+', '', wordsList[w])
                dictionary = open(filename).readlines()
                dictionary = map(lambda x: x.strip(), dictionary)
                if wordsList[w] not in dictionary:
                	misspelledWords.append(wordsList[w])

            flash('The following words are misspelled: ' + str(misspelledWords))
        else:
            flash('Cannot leave the field blank. ')

        return render_template('hello.html', form=form)

if __name__ == "__main__":
    app.run()