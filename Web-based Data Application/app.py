import os
import pickle

from flask import Flask, render_template, request, redirect, session
from gensim.models.fasttext import FastText
from bs4 import BeautifulSoup
import pandas as pd
from utils import gen_docVecs

app = Flask(__name__)
app.secret_key = os.urandom(16) 

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/Accounting_Finance')
def Accounting():
    return render_template('accounting_finance.html')

@app.route('/Engineering')
def Engineering():
    return render_template('engineering.html')

@app.route('/Healthcare_Nursing')
def Healthcare():
    return render_template('healthcare_nursing.html')

@app.route('/Hospitality_Catering')
def Hospitality():
    return render_template('hospitality_catering.html')

@app.route('/IT')
def IT():
    return render_template('it.html')

@app.route('/PR_Advertising_Marketing')
def PR():
    return render_template('pr_advertising_marketing.html')

@app.route('/Sales')
def Sales():
    return render_template('sales.html')

@app.route('/Teaching')
def Teaching():
    return render_template('teaching.html')

@app.route('/about')
def about():
    return render_template('about.html')
    

@app.route('/<folder>/<filename>')
def article(folder, filename):
    return render_template('/' + folder + '/' + filename + '.html')

@app.route("/admin", methods=['GET', 'POST']) 
def admin():
    if 'username' in session:
        if request.method == 'POST':

            # Read the .txt file
            f_title = request.form['title'].lower()
            f_salary = request.form['salary']

            f_content = request.form['description']

            # Classify the content
            if request.form['button'] == 'Classify':

                # Tokenize the content of the .txt file so as to input to the saved model 
                tokenized_data = f_content.split(' ')

                # Load the FastText model
                jobFT = FastText.load("jobsFT.model")
                jobFT_wv= jobFT.wv

                # Generate vector representation of the tokenized data
                jobFT_dvs = gen_docVecs(jobFT_wv, [tokenized_data])

                # Load the LR model
                pkl_filename = "jobsFT_LR.pkl"
                with open(pkl_filename, 'rb') as file:
                    model = pickle.load(file)

                # Predict the label of tokenized_data
                y_pred = model.predict(jobFT_dvs)
                y_pred = y_pred[0]

                return render_template('admin.html', prediction=y_pred, title=f_title, salary= f_salary,description=f_content)

            elif request.form['button'] == 'Save':

                # First check if the recommended category is empty
                cat_recommend = request.form['category']
                if cat_recommend == '':
                    return render_template('admin.html', prediction=cat_recommend,
                                        title=f_title, description=f_content,
                                        category_flag='Recommended category must not be empty.')

                elif cat_recommend not in ['Accounting_Finance', 'Engineering', 'Healthcare_Nursing','Hospitality_Catering', 'IT', 'PR_Advertising_Marketing','Sales','Teaching']:
                    return render_template('admin.html', prediction=cat_recommend,
                                        title=f_title, description=f_content,
                                        category_flag='Recommended category must belong to: Accounting_Finance, Engineering, Healthcare_Nursing, Hospitality_Catering, IT, PR_Advertising_Marketing, Sales, Teaching.')

                else:

                    # First read the html template
                    soup = BeautifulSoup(open('templates/article_template.html'), 'html.parser')
                    
                    # Then adding the title and the content to the template
                    # First, add the title
                    div_page_title = soup.find('div', { 'class' : 'title' })
                    title = soup.new_tag('h1', id='data-title')
                    title.append(f_title)
                    div_page_title.append(title)

                    div_page_title = soup.find('div', { 'class' : 'salary' })
                    salary = soup.new_tag('h1', id='data-salary')
                    salary.append(f_salary)
                    div_page_title.append(salary)

                    # Second, add the content
                    div_page_content = soup.find('div', { 'class' : 'data-article' })
                    content = soup.new_tag('p')
                    content.append(f_content)
                    div_page_content.append(content)

                    # Finally write to a new html file
                    filename_list = f_title.split()
                    filename = '_'.join(filename_list)
                    filename =  cat_recommend + '/' + filename + ".html"
                    with open("templates/" + filename, "w", encoding='utf-8') as file:
                        print(filename)
                        file.write(str(soup))

                    # Clear the add-new-entry form and ask if user wants to continue to add new entry
                    return redirect('/' + filename.replace('.html', ''))

        else:
            return render_template('admin.html')
    else:
        return redirect('/login')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        if (request.form['username'] == 'COSC2820') and (request.form['password'] == 'TestingRMIT'):
            session['username'] = request.form['username']
            return redirect('/admin')
        else:
            return render_template('login.html', login_message='Username or password is invalid.')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)

    return redirect('/')


@app.route('/search', methods = ['POST'])
def search():

    if request.method == 'POST':
    
        if request.form['search'] == '':
            search_string = request.form["searchword"]

            # search over all the html files in templates to find the search_string
            article_search = []
            dir_path = 'templates'
            for folder in os.listdir(dir_path):
                if os.path.isdir(os.path.join(dir_path, folder)):
                    for filename in sorted(os.listdir(os.path.join(dir_path, folder))):
                        if filename.endswith('html'):
                            with open(os.path.join(dir_path, folder, filename), encoding="utf8") as file:
                                file_content = file.read()

                                # search for the string within the file
                                if search_string in file_content:
                                    article_search.append([folder, filename.replace('.html', '')])
            
            # generate the right format for the Jquery script in search.html
            num_results = len(article_search)

            # exact search or related search (regex, stemming or lemmatizing)

            # can handle the case when no search results

            # search both titles and descriptions

            return render_template('search.html', num_results=num_results, search_string=search_string,
                                   article_search=article_search)
    
    else:
        return render_template('home.html')

#USED TO LOAD THE WEBSITE
if __name__ == '__main__':
    app.run(debug=True)


