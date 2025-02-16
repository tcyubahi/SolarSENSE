/*
	Author: ASU CAPSTONE TEAM 2018
	Date: 11.08.2018
	Description: Controllers for Handling UI data binding and REST request
*/

var env = {};

if(window){
	Object.assign(env, window.__env);
}

var app = angular.module('solarsenseApp', []);

app.constant("__env", env);

app.config(['$interpolateProvider', function($interpolateProvider) {
  	$interpolateProvider.startSymbol('{a');
  	$interpolateProvider.endSymbol('a}');
}]);

app.controller('ConfigCtrl', function($scope,$http,$timeout){

	$scope.hasNumOfFields = false;
	$scope.numOfFields = "";
	$scope.fieldCount = 0;
	$scope.saveMessage = "";
	$scope.saveSuccessful = false;
	$scope.fields = [];

	$scope.showFields = function() {
		if ($scope.numOfFields > 0){
			$scope.hasNumOfFields = true;
		} 
	};

	$scope.displayFields = function(){

		if(parseInt($scope.numOfFields) !== 0
			&& parseInt($scope.numOfFields) <= 10
			&& $scope.numOfFields !== undefined
			&& !isNaN(parseInt($scope.numOfFields))) {
			var fields = parseInt($scope.numOfFields,10);
			$scope.fieldCount = fields;
			$scope.hasNumOfFields = true;
			$scope.generateFieldEntries();
			console.log($scope.fields.length);
		} else {
			$scope.hasNumOfFields = false;
			$scope.fieldMax(parseInt($scope.numOfFields));
		}
	};

	$scope.generateFieldEntries = function(){
		$scope.fields = new Array($scope.fieldCount);
	};

	$scope.fieldMax = function(){
		if($scope.fieldCount > 100){
			$scope.maxMsg = "Number is not valid, must be less than 100!";
			return true;
		}
		return false;
	};

	$scope.resetMaxMsg = function(){
		$scope.maxMsg = "";
	};

	$scope.saveFieldSettings = function(){

		var saveFieldCount = $scope.fieldCount;
		var fieldNames = document.getElementsByName("fieldName");
		var saveArray = new Array();

		var fieldNumber = document.getElementById("numOfFieldsInput").value;
		console.log("Test Value: "+ parseInt(fieldNumber));

		if(!isNaN(parseInt(fieldNumber))){
			for(var i = 0; i < fieldNames.length; i++){
				var nameObj = {
					"fieldName" : fieldNames[i].value
				}
				saveArray.push(nameObj);
			}

			console.log(saveArray);

			var saveObj = {
				"numOfFields" : saveFieldCount,
				"fieldNames" : saveArray
			};

			$http({
				method: 'POST',
				url: __env.serverUrl + '/setFields',
				data: saveObj,
				headers: {
					'Access-Control-Allow-Origin': '*',
	        		'Access-Control-Allow-Methods' : 'POST',
	        		'Access-Control-Allow-Headers' : 'Content-Type, Authorization, Content-Length, X-Requested-With'
				}
			}).then(function success(response){
				var res = response.data;
				console.log(res);
				$scope.saveMessage = res['message'];
				$scope.saveSuccessful = true;
				$scope.numOfFields = "";
				$scope.hasNumOfFields = false;
			}, function error(resposne){
				console.log("There was an error");
			});
		} else {
			$scope.saveMessage = "Invalid input in number of fields. Please Check Entry and try again."
			$scope.saveSuccessful = true;
			return;
		}
	};

	$scope.didSave = function() {
		if($scope.saveSuccessful){
			return true;
		} else {
			return false;
		}
	};

	$scope.resetSaveAlert = function() {
		$scope.saveSuccessful = false;
	};
});
