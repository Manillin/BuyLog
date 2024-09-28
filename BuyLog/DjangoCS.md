# Django Cheat Sheet



## StartUp progetto


### Comandi Shell:

```bash
mkdir ProjectFolder
cd ProjectFolder

pipenv install django 
pipenv shell

django-admin startproject nomeprogetto
cd nomeprogetto

python manage.py runserver #per lanciare il server web

# se si vuole creare un app per gestire particolare necessita:
python manage.py startapp nomeapp 

```

E sistemare i seguenti setting: 

### Comandi dentro il Workspace:

Una volta creato il workspace con i realtivi folder ricordarsi di apportare le seguenti modifiche:
1. Creare i folder dei template in `nomeprogetto/templates` e se abbiamo creato un app anche in `nomeapp/templates/nomeapp`  
2. In `settings.py`:
    - aggiungere in `INSTALLED_APPS` il nome dell'app, braces, crispyforms e in `TEMPLATES` aggiungere `DIRS:[os.path.join(BASE_DIR), "templates"]`.  
3. Creare i modelli e applicare le migrazioni con i seguenti due comandi:
    - `python manage.py makemigrations nomeapp`
    - `python manage.py migrate`
4. Se si vuole inizializzare il DB creare uno script `nomeprogetto/initcmd.py` e creare `init_db()` e `erase_db()`.  
5. Creare un **Superutente**:  
    - `python manage.py createsuperuser` e seguire le istruzioni da terminale  
    - In nomeapp/admin.py registrare i modelli `admin.site.register(Modello)`



--- 


# Django Views: 

## CreateView:
Una vista generica di Django utilizzata per creare nuovi oggetti nel database. 


### Funzionamento e Workflow:
Quando si utilizza una `CreateView`, Django segue in ordine i seguenti passaggi: 
1. **Visualizzazione del Form:** Quando l'utente accede alla pagina linkata a questa view, Django visualizza il form definito in form_class
2. **Invio del Form:** Quando l'utente invia il form, Django valida i dati e solo una volta validati _crea_ l'oggetto nel DB. 
3. **Redirezione:** Dopo aver creato l'oggetto, Django redirige l'utente all'url di successo


### Definizione: 

```python
class CreateGenericView(CreateView):
    template_name = "source/templatename.html"
    form_class = CustomFormModel
    success_url = 'root:path1'

    def get_success_url(self):
        ctx = self.get_context_data()
        pk = ctx["object"].model.pk
        return reverse("polls:detail", kwargs={"pk": pk})
```

### Spiegazione Attributi e Metodi:
- `template_name`: Specifica il template che invocherà per il rendering della CBV
- `form_class`:  Specifica il modello specifico che abbiamo linkato alla view, spesso è un FormModel (in particolare se vogliamo creare una entry nel DB )
- `success_url`: url target di redirezione una volta che il form viene validato e superato senza errori
- `def get_success_url(self):` Override del metodo default per ottenere l'url, utile in situazioni in cui vogliamo fare un redirect **dinamico**. Se la nostra CreateView crea un nuovo oggetto e il link dinamico richiede la pk (o qualsiasi altro attributo) dell'oggetto possiamo fare come nell'esempio! Ricordiamo che non possiamo farlo tra gli attributi della classe in quanto essi sono valutati al momento della definizione dell classe e non al momento della creazione dell'oggetto! per questo con get_context_data() possiamo ottenere l'oggetto creato, dato che viene invocato dopo la creazione!!





# Django Forms & ModelForms: 

Classe Django che permette di creare Form personalizzati, definendo i campi manualmente e gestendo la validazione di input e salvataggio dei dati.  

## ModelForm:
Sottoclasse di Form che crea automaticamente un form basato su un modello esistente. I campi del form sono generati automaticamente in base ai campi del modello $\rightarrow$ Utile quando si vuole creare o aggiornare un istanza di un modello, riducendo il codice boilerplate.  

```python
from django import forms 
from .models import * 

class ModelForm(forms.ModelForm):

```


### Dettagli e Parametri:

### `clean`

Il metodo **`clean`** è un metodo di default nei form di Django che viene utilizzato per la validazione personalizzata dei dati del form. Quando definisci il metodo clean all'interno di un form, stai effettivamente sovrascrivendo il metodo di default per aggiungere la tua logica di validazione personalizzata.

Il metodo clean viene chiamato automaticamente durante il processo di validazione del form, dopo che i singoli campi sono stati validati.
- Accesso ai Dati Puliti: Utilizza `self.cleaned_data` per accedere ai dati del form che sono stati già validati e puliti.
- Aggiunta di Errori: Puoi aggiungere errori specifici ai campi utilizzando `self.add_error(field, error_message)`.