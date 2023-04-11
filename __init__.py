from flask import Flask, jsonify, request
app = Flask(__name__)
#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "HolaNovato":
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."
    #RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data=request.get_json()
    #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
    telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    #EXTRAEMOS EL TELEFONO DEL CLIENTE
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    #SI HAY UN MENSAJE
    if mensaje is not None:
      
        import openai
        # Indica el API Key
        openai.api_key = "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"
        # Uso de ChapGPT en Python
        model_engine = "text-davinci-003"
        prompt = mensaje
        completion = openai.Completion.create(engine=model_engine,
                                            prompt=prompt,
                                            max_tokens=1024,
                                            n=1,
                                            stop=None,
                                            temperature=0.7)
        respuesta=""
        for choice in completion.choices:
            respuesta=respuesta+choice.text
            print(f"Response: %s" % choice.text)

        respuesta=respuesta.replace("\\n","\\\n")
        respuesta=respuesta.replace("\\","")
        #CONECTAMOS A LA BASE DE DATOS
        import mysql.connector
        mydb = mysql.connector.connect(
          host = "localhost",
          user = "root",
          password = "",
          database='novato_chat'
        )
        mycursor = mydb.cursor()
        query="SELECT count(id) AS cantidad FROM registro WHERE id_wa='" + idWA + "';"
        mycursor.execute(query)

        cantidad, = mycursor.fetchone()
        cantidad=str(cantidad)
        cantidad=int(cantidad)
        if cantidad==0 :
            sql = ("INSERT INTO registro"+ 
            "(mensaje_recibido,mensaje_enviado,id_wa      ,timestamp_wa   ,telefono_wa) VALUES "+
            "('"+mensaje+"'   ,'"+respuesta+"','"+idWA+"' ,'"+timestamp+"','"+telefonoCliente+"');")
            mycursor.execute(sql)
            mydb.commit()        
            enviar(telefonoCliente,respuesta)
        #RETORNAMOS EL STATUS EN UN JSON
        return jsonify({"status": "success"}, 200)
def enviar(telefonoRecibe,respuesta):
  from heyoo import WhatsApp
  #TOKEN DE ACCESO DE FACEBOOK
  token='EAALDlRZBLBD4BAGIFXLcPuwwgkXMZAnCOAuvPTXRBPbi4tKavrq9PmCFuWfMvmoBHkjeKghBQhs0AExdK3Ru5NCXfWsDaIvUuVAZBDLNtKmom0pwSkA9LhUJMYrLVYTLhlWPPjg9iRuOBSpKKr7oExDHwC385UxJZCwFH2qxadMfqKQDAMMngReZBNvyJ3rLFmiOVB6xZBrwZDZD'
  #IDENTIFICADOR DE NÚMERO DE TELÉFONO
  idNumeroTeléfono='116907067953774'
  #INICIALIZAMOS ENVIO DE MENSAJES
  mensajeWa=WhatsApp(token,idNumeroTeléfono)
  telefonoRecibe=telefonoRecibe.replace("521","52")
  #ENVIAMOS UN MENSAJE DE TEXTO
  mensajeWa.send_message(respuesta,telefonoRecibe)
#INICIAMSO FLASK
if __name__ == "__main__":
  app.run(debug=True)
