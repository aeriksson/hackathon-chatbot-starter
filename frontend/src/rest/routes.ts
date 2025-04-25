// Empty routes file - route loading is now simplified in the API client
export interface Route {
    path: string;
    module: any;
}

export const routes: Route[] = [];