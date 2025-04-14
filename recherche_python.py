import networkx as nx
import time

start = time.time()



graph = nx.Graph()

with open("graph.txt") as fichierTest : 
    for ligne in fichierTest : 
        n1 , n2 = ligne.split()
        graph.add_nodes_from([n1,n2])
        graph.add_edge(n1 , n2 , weight = 1)

print("graph chargé : " , len(graph.nodes), " noeuds et " ,len(graph.edges) , " arêtes.")




def calcul_sigma_in(membres_commu) : 
    sigma_in = 0
    for u in membres_commu :
        for v in membres_commu :
            if graph.has_edge(u,v) :
                sigma_in += graph[u][v].get('weight', 1)
    return sigma_in

def calcul_impact_node(node , membres_commu) : 
    impact = 0
    for v in membres_commu : 
        if graph.has_edge(node,v) :
            impact += graph[node][v].get('weight' , 1)
    return impact


def calcul_ki_in(node , community) :
    voisins = graph.neighbors(node) 
    ki_in = 0
    for v in voisins : 
        if v in communities[community] :
            ki_in += graph[node][v].get('weight', 1)
    return ki_in

m = sum(data.get('weight', 1) for u, v, data in graph.edges(data=True))
print(m)
def calcul_delta(graph , node , commu) :
    sigma_in = dict_commu_in[commu] #poids total des arêtes internes à la communauté C (nb d'arêtes internes pour un graph non pondéré)
    ki_in = calcul_ki_in(node , commu) #poids total des arêtes entre node et la cummunauté C (nb voisins de node dans C pour un graph non pondéré)
    ki = graph.degree[node] #degré de node
    sigma_tot = dict_commu_tot[commu] #degré total de C (Somme des deg de tous ses noeuds)

    part1 = ((sigma_in + ki_in)/(2*m)) - (((sigma_tot + ki)/(2*m))**2)
    part2 = (sigma_in / (2*m)) - ((sigma_tot/(2*m))**2) - ((ki/(2*m))**2)
    delta = part1 - part2
    return delta



communities = {}
noeud_commu = {}
dict_commu_tot = {}
dict_commu_in = {}
dict_degres = dict(graph.degree())
#m = graph.number_of_edges() #poids total des arêtes du graphe (nb des arêtes pour un graph non pondéré)

i = 0
for node in graph.nodes :
    noeud_commu[node] = i
    community_members = set()
    community_members.add(node)
    communities[i] = community_members
    sigma_in = calcul_sigma_in(community_members)
    sigma_tot = dict_degres[node]
    dict_commu_in[i] = sigma_in
    dict_commu_tot[i] = sigma_tot
    i += 1
    

SEUIL_DELTA = 1e-5 #La modularité commece à 2.xxe-5 donc un seuil plus grand bloque tous les calculs , à voir plus tard avec le merge
changement = True
while  len(communities) > 595: #L'algo boucle à l'infini à partir de 595 commus pour l'instant , il faut la dexième phase
    changement = False
    compteur = 0
    for node in graph.nodes :
        old_community = noeud_commu[node]
        gain_modularite = 0.0
        new_community = old_community
        voisins = graph.neighbors(node)
        commu_voisines = set()
        for v in voisins :
            commu_voisines.add(noeud_commu[v])                

        for commu in commu_voisines :
            delta = calcul_delta(graph , node , commu)
            if delta > gain_modularite and delta > SEUIL_DELTA:
                gain_modularite = delta
                new_community = commu
        if new_community != old_community :
            #Modifier la valeur de noeud_commu[node] 
            #Supprimer node du set de membres de old_community et l'ajouter au set de membres de new_commu
            communities[new_community].add(node)
            communities[old_community].remove(node)
            #Il faut mettre à jour les valeurs de sigma_in et sigma_tot dans les dict des deux commus
            dict_commu_in[new_community] +=  calcul_impact_node(node , communities[new_community])
            dict_commu_tot[new_community] = dict_commu_tot[new_community] + dict_degres[node]
            if not communities[old_community] :
                del communities[old_community]
                del dict_commu_in[old_community]
                del dict_commu_tot[old_community]
            else : 
                dict_commu_in[old_community] -= calcul_impact_node(node , communities[old_community])
                dict_commu_tot[old_community] = dict_commu_tot[old_community] - dict_degres[node]
            noeud_commu[node] = new_community
            changement = True
        
            
            
        compteur +=1 

    #with open("results/resultats"+str(i)+".txt", "w") as f:
    #    print(communities, file=f)    
    
    #changement = False    

end = time.time()
print("Temps d'execution :", end - start, "secondes")