import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:video_player/video_player.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_onboard/flutter_onboard.dart';
import 'dart:convert' as convert;
import 'globals.dart' as globals;


void main() {
  runApp(MaterialApp(
    initialRoute: '/',
    routes: {
      '/': (context) => Opening(),
      '/second': (context) => MyHomePage(),
    },
  ));
}

class Home extends StatelessWidget {

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.purple,
        primaryColor: Colors.deepPurple,
      ),
      home: Opening(),
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


    final request = http.MultipartRequest("POST", Uri.parse("https://ae26-24-133-127-30.eu.ngrok.io/upload"));
    final headers = {"Content-type": "multipart/form-data"};

    request.files.add(http.MultipartFile('image', selectedImage!.readAsBytes().asStream(), selectedImage!.lengthSync(),
        filename:  selectedImage!.path.split("/").last));
    request.fields['liquid'] = globals.dropdownValue;

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
        backgroundColor: Colors.deepPurple,
      ),
      body: LayoutBuilder(
        builder: (context, constraints) => Column(
          children: [
            SizedBox(height: 100),
            Text(
              "Select liquid:",
              style: TextStyle(fontSize: 18.0),
            ),
            SizedBox(
              width: 100,
              height: 50,
              child: MyStatefulWidget(),
            ),
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(64.0),
                child: Column(
                  children: <Widget>[
                    if (_video != null)
                      Text(
                        "Please wait for the server",
                        style: TextStyle(fontSize: 18.0),
                      )
                    else
                      Text(
                        "Click on Pick Video to select video",
                        style: TextStyle(fontSize: 18.0),
                      ),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        primary: Colors.purple
                      ),
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
          ],
        ),
      ),
    );
  }
}

class MyStatefulWidget extends StatefulWidget {
  const MyStatefulWidget({Key? key}) : super(key: key);

  @override
  State<MyStatefulWidget> createState() => _MyStatefulWidgetState();
}

class _MyStatefulWidgetState extends State<MyStatefulWidget> {

  @override
  Widget build(BuildContext context) {
    return DropdownButton<String>(
      value: globals.dropdownValue,
      icon: const Icon(Icons.arrow_downward),
      elevation: 16,
      style: const TextStyle(color: Colors.deepPurple),
      underline: Container(
        height: 2,
        color: Colors.deepPurpleAccent,
      ),
      onChanged: (String? newValue) {
        setState(() {
          globals.dropdownValue = newValue!;
        });
      },
      items: <String>['Water', 'Cologne']
          .map<DropdownMenuItem<String>>((String value) {
        return DropdownMenuItem<String>(
          value: value,
          child: Text(value),
        );
      }).toList(),
    );
  }
}

class Opening extends StatelessWidget{
  final PageController _pageController = PageController();
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: OnBoard(
        pageController: _pageController,
        // Either Provide onSkip Callback or skipButton Widget to handle skip state
        onSkip: () {
          // print('skipped');
        },
        // Either Provide onDone Callback or nextButton Widget to handle done state
        onDone: () {
          // print('done tapped');
        },
        onBoardData: onBoardData,
        titleStyles: const TextStyle(
          color: Colors.deepPurple,
          fontSize: 18,
          fontWeight: FontWeight.w900,
          letterSpacing: 0.15,
        ),
        descriptionStyles: TextStyle(
          fontSize: 16,
          color: Colors.brown.shade300,
        ),
        pageIndicatorStyle: const PageIndicatorStyle(
          width: 100,
          inactiveColor: Colors.deepPurpleAccent,
          activeColor: Colors.deepPurple,
          inactiveSize: Size(8, 8),
          activeSize: Size(12, 12),
        ),
        // Either Provide onSkip Callback or skipButton Widget to handle skip state
        skipButton: TextButton(
          onPressed: () {
            Navigator.pushNamed(context, '/second');
          },
          child: const Text(
            "Skip",
            style: TextStyle(color: Colors.deepPurpleAccent),
          ),
        ),
        // Either Provide onDone Callback or nextButton Widget to handle done state
        nextButton: OnBoardConsumer(
          builder: (context, ref, child) {
            final state = ref.watch(onBoardStateProvider);
            return InkWell(
              onTap: () => _onNextTap(state),
              child: Container(
                width: 230,
                height: 50,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(30),
                  gradient: const LinearGradient(
                    colors: [Colors.deepPurpleAccent, Colors.purpleAccent],
                  ),
                ),
                child: Text(
                  state.isLastPage ? "" : "Next",
                  style: const TextStyle(
                    color: Colors.black,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
  void _onNextTap(OnBoardState onBoardState) {
    if (!onBoardState.isLastPage) {
      _pageController.animateToPage(
        onBoardState.page + 1,
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeInOutSine,
      );
    } else {
      //print("nextButton pressed");
    }
  }
}
final List<OnBoardModel> onBoardData = [
  const OnBoardModel(
    title: "Be mindful of where you put the coin",
    description: "The coin should be at the top left quarter of the frame, away from the petri dish",
    imgUrl: "assets/coinloc.jpg",
  ),
  const OnBoardModel(
    title: "Take at least 2 min videos(3 preferred)",
    description:
    "",
    imgUrl: 'assets/2-3Min.jpg',
  ),
];