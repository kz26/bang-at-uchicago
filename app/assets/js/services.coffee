app = angular.module('app', [])
	.config ($routeProvider) ->
		$routeProvider
			.when('/', {templateUrl: '/static/js/partials/index.html', controller: SplashCtrl})
			.when('/down/to/bang', {templateUrl: '/static/js/partials/register.html', controller: RegisterCtrl})
			.when('/wait/to/bang', {templateUrl: '/static/js/partials/registered.html', controller: NullCtrl})
			.when('/start/banging', {templateUrl: '/static/js/partials/login.html', controller: LoginCtrl})
			.when('/you/can/start/banging', {templateUrl: '/static/js/partials/activated.html', controller: NullCtrl})
			.when('/forgot/how/to/bang', {templateUrl: '/static/js/partials/forgot-password.html', controller: ForgotPassCtrl})
			.when('/remember/how/to/bang', {templateUrl: '/static/js/partials/reset-password.html', controller: ResetPassCtrl})
			.when('/stop/banging', {template: 'logout', controller: LogoutCtrl})
			.when('/my/fucking/account', {templateUrl: '/static/js/partials/my-account.html', controller: MyAccountCtrl})
			.when('/who/i/want/to/bang', {templateUrl: '/static/js/partials/bangList.html', controller: BangCtrl})
			.when('/also/want/to/bang', {templateUrl: '/static/js/partials/bangMatches.html', controller: BangMatchCtrl})
			.when('/my/bangability', {templateUrl: '/static/js/partials/bangScore.html', controller: BangScoreCtrl})
			.when('/privacy', {templateUrl: '/static/js/partials/privacy-policy.html', controller: NullCtrl})
			.when('/most/bangable', {templateUrl: '/static/js/partials/most-bangable.html', controller: MostBangableCtrl})
			.otherwise('/')
	.run ($rootScope, $http, $location) ->
		$http.get("/auth-info/")
			.success (data) ->
				$rootScope.user = data
				if (1 in data.groups)
					$rootScope.user.inner_circle = true
				$location.path "/who/i/want/to/bang"
			.error ->
        		$rootScope.user = null
