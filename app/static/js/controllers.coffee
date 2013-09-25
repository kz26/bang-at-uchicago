NullCtrl = ($rootScope) ->

SplashCtrl = ($rootScope, $location) ->
	if $rootScope.user
		$location.path "/who/i/want/to/bang"
		$location.replace()
		return
	$rootScope.showNav = false

NavCtrl = ($rootScope, $scope, $location) ->
	$scope.pages = [
		{name: "My Bang List", url: "#/who/i/want/to/bang"},
		{name: "My Bang Matches", url: "#/also/want/to/bang"},
		{name: "My Bangability Score", url: "#/my/bangability"}
	]
	$scope.activeCSS = (url) ->
		if "#" + $location.path() == url
			return "active"
		return ""
	
RegisterCtrl = ($rootScope, $scope, $http, $location) ->
	if $rootScope.user
		$location.path "/who/i/want/to/bang"
		$location.replace()
		return
	$rootScope.showNav = false

	$scope.user = {username: "", password: "", passwordConfirm: ""}
	$scope.errors = null

	$scope.resetError = (field, key) ->
		$scope.form[field].$setValidity(key, true)

	$scope.submit = ->
		data = angular.copy($scope.user)
		$http.post("/register/", data)
			.success ->
				$scope.errors = null
				$location.path "/wait/to/bang"
			.error (data) ->
				$scope.errors = data
				if 'username' of data
					$scope.form.username.$setValidity('invalidCnetId', false)
				if 'password' of data
					$scope.form.password.$setValidity('invalid', false)


LoginCtrl = ($rootScope, $scope, $http, $location) ->
	if $rootScope.user
		$location.path "/who/i/want/to/bang"
		$location.replace()
		return
	$rootScope.showNav = false

	$scope.user = {username: "", password: ""}
	$scope.errors = null
	$scope.submit = ->
		$http.post("/login/", $scope.user)
			.success (data) ->
				$scope.errors = null
				$rootScope.user = data
				$rootScope.show_hidden_pages = ('inner_circle' in data.groups)
				$location.path "/who/i/want/to/bang"
			.error (data) ->
				$scope.errors = data

LogoutCtrl = ($rootScope, $http, $location) ->
	$http.get("/logout/")
		.success ->
			$rootScope.user = null
			$location.path "/"

ForgotPassCtrl = ($rootScope, $scope, $http, $location) ->
	if $rootScope.user
		$location.path "/who/i/want/to/bang"
		$location.replace()
		return
	$rootScope.showNav = false

	$scope.resetError = ->
		$scope.form.username.$setValidity('invalid', true)
	$scope.submit = ->
		$http.post("/forgot-password/", {username: $scope.username})
			.success ->
				$scope.success = true
			.error (data) ->
				$scope.success = false
				$scope.errors = data
				$scope.form.username.$setValidity('invalid', false)
		
ResetPassCtrl = ($rootScope, $scope, $http, $location) ->
	if $rootScope.user
		$location.path "/who/i/want/to/bang"
		$location.replace()
		return
	$rootScope.showNav = false

	key = $location.search().key
	$scope.data = {key: key, password: "", passwordConfirm: ""}

	$scope.resetError = (field, key) ->
		$scope.form[field].$setValidity(key, true)

	$scope.submit = ->
		$http.post("/reset-password/", $scope.data)
			.success ->
				$scope.success = true
			.error (data) ->
				$scope.errors = data
				if 'password' of data
					$scope.form.password.$setValidity('invalid', false)

MyAccountCtrl = ($rootScope, $scope, $http, $location) ->
	if not $rootScope.user
		$location.path "/"
		$location.replace()
		return
	$rootScope.showNav = false

	$scope.resetError = (form, field, key) ->
		$scope[form][field].$setValidity(key, true)

	$scope.profile = {}
	$http.get("/profile/")
		.success (data)->
			$scope.profile = data
	$scope.updateProfile = ->
		$http.put("/profile/", {optout: parseInt($scope.profile.optout)})
			.success ->
				$scope.profileUpdated = true
			.error ->
				$scope.profileUpdateError = false

	$scope.passData = {}
	$scope.changePassword = ->
		$http.post("/change-password/", $scope.passData)
			.success ->
				$scope.pwChanged = true
				$scope.passData = {}
			.error (data) ->
				$scope.pwChanged = false
				$scope.pwChangeErrors = data
				if 'old_password' of data
					$scope.pwChangeForm.old_password.$setValidity('invalid', false)
				if 'password' of data
					$scope.pwChangeForm.password.$setValidity('invalid', false)

BangCtrl = ($rootScope, $scope, $http, $location) ->
	if not $rootScope.user
		$location.path "/"
		$location.replace()
		return
	$rootScope.showNav = true

	$scope.searchQuery = {cnetid: "", first_name: "", last_name: ""}
	$scope.searchQueryError = null
	$scope.searchResults = null
	$scope.showFap = false

	$scope.submitText = "Hit me!"

	$scope.myBangs = []

	$scope.isFormValid = ->
		return $scope.searchQuery.cnetid or ($scope.searchQuery.first_name and $scope.searchQuery.last_name)
	$scope.search = ->
		$scope.showFap = false
		if $scope.searchQuery.cnetid or ($scope.searchQuery.first_name and $scope.searchQuery.last_name)
			if $scope.searchQuery.cnetid == $rootScope.user.cnetid
				$scope.showFap = true
				return
			$scope.searchQueryError = null
			$http.get("/bangs/search/", {params: $scope.searchQuery})
				.success (data) ->
					$scope.searchResults = data
					$scope.searchQueryError = null
					if not data.length and ($scope.searchQuery.first_name == $rootScope.user.first_name and $scope.searchQuery.last_name == $rootScope.user.last_name)
						$scope.showFap = true
					$scope.submitText = "Hit me one more time, baby!"
				.error (data) ->
					$scope.searchQueryError = data
				.then ->
					$scope.searchQuery = {cnetid: "", first_name: "", last_name: ""}
					
		else
			$scope.searchQueryError = true

	$scope.addBang = (user) ->
		$http.post("/bangs/new/", {id: user.id})
			.success (data) ->
				$scope.myBangs.unshift(data)
				$scope.searchResults.splice($scope.searchResults.indexOf(user), 1)
	
	$scope.unBang = (bang) ->
		if bang.can_unbang
			$http.post("/bangs/delete/", {id: bang.id})
				.success ->
					$scope.myBangs.splice($scope.myBangs.indexOf(bang), 1)
				.error (data, status) ->
					if status == 404
						$scope.myBangs.splice($scope.myBangs.indexOf(bang), 1)

	$scope.getTooltip = (bang) ->
		if bang.can_unbang
			return "Don't want to bang this person anymore? Click to remove them from your Bang List."
		else
			return "You can't pull out yet, you're not done! Wait 24 hours to remove this user from your Bang List."

	$http.get("/my/bangs/")
		.success (data) ->
			$scope.myBangs = data
	
BangMatchCtrl = ($rootScope, $scope, $http, $location) ->
	if not $rootScope.user
		$location.path "/"
		$location.replace()
		return
	$rootScope.showNav = true

	$http.get("/my/bangs/matches/")
		.success (data) ->
			$scope.myBangMatches = data

	$scope.getReadCSS = (read) ->
		if read
			return ''
		return 'success'

BangScoreCtrl = ($rootScope, $scope, $http, $location) ->
	if not $rootScope.user
		$location.path "/"
		$location.replace()
		return
	$rootScope.showNav = true

	$http.get("/my/bangability/")
		.success (data) ->
			$scope.scoreData = data

MostBangableCtrl = ($rootScope, $scope, $http, $location) ->
	if not $rootScope.user or not ($rootScope.show_hidden_pages)
		$location.path "/"
		$location.replace()
		return
	$rootScope.showNav = false
	
	$http.get("/most/bangable/")
		.success (data) ->
			$scope.users = data
