import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_player/video_player.dart';
import 'package:http/http.dart' as http;
import 'dart:convert' as convert;


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {

  File? selectedImage;

  String message = "";

  File? _video;

  String greetings = "";

  ImagePicker picker = ImagePicker();

  VideoPlayerController? _videoPlayerController;

  // This function helps picking a Video File
  _pickVideo() async {
    XFile? pickedFile = await picker.pickVideo(source: ImageSource.gallery);
    _video = File(pickedFile!.path);

    selectedImage = _video;

    _videoPlayerController = VideoPlayerController.file(_video!)
      ..initialize().then((_) {
        setState(() {});
        _videoPlayerController!.play();
      });

    final request = http.MultipartRequest("POST", Uri.parse("https://9f9a-24-133-127-30.eu.ngrok.io/upload"));
    final headers = {"Content-type": "multipart/form-data"};

    request.files.add(http.MultipartFile('image', selectedImage!.readAsBytes().asStream(), selectedImage!.lengthSync(),
    filename:  selectedImage!.path.split("/").last));

    request.headers.addAll(headers);
    final response = await request.send();
    http.Response res = await http.Response.fromStream(response);
    final resJson = convert.jsonDecode(res.body);
    message = resJson['message'];
    print(resJson['message']);
    setState(() {});
    //var url = Uri.parse('http://10.0.2.2:5000');
    // http.Response response = await http.get(url);
    // final decoded = json.decode(response.body) as Map<String, dynamic>;
    // setState(() {
    //   greetings = decoded['query'];
    // });
    // print(greetings);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Viscometer"),
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Container(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: <Widget>[
                if (_video != null)
                  _videoPlayerController!.value.isInitialized
                      ? AspectRatio(
                    aspectRatio: _videoPlayerController!.value.aspectRatio,
                    child: VideoPlayer(_videoPlayerController!),
                  )

                      : Container()
                else
                  Text(
                    "Click on Pick Video to select video",
                    style: TextStyle(fontSize: 18.0),
                  ),
                ElevatedButton(
                  onPressed: () {
                    _pickVideo();
                  },
                  child: Text("Pick Video From Gallery"),
                ),
                Text(message,
                  style: TextStyle(fontSize: 18.0),),
              ],
            ),

          ),
        ),
      ),
    );
  }
}