
program test
    use data_model
    use input_output
    use execution_model
    use linear_algebra
    implicit none
    
    type(t_mdb)      :: mdb
    type(t_element)  :: element
    type(t_section)  :: section
    type(t_material) :: material

    type(t_sparse) :: Kaa, Kab
    type(t_matrix), allocatable :: Ks(:)
    integer :: i, j, il, ig, jl, jg
    
    real :: load(50), x(50)
    
    
    integer :: pt(64), maxfct, mnum, mtype, phase, n, nrhs, iparm(64), msglvl, error
    integer, allocatable :: perm(:)
    real lol
    
    mdb = read_input('C:/Users/Carlos/Desktop/data.txt')
    
    allocate(Ks(mdb%mesh%n_elements))
    Kaa = new_sparse(mdb%n_adofs, mdb%n_adofs)
    Kab = new_sparse(mdb%n_adofs, mdb%n_idofs)
    
    do i = 1, mdb%mesh%n_elements
        element  = mdb%mesh%elements(i)
        section  = mdb%sections(element%i_section)
        material = mdb%materials(section%i_material)
        Ks(i) = e_get_K(element, section, material, mdb%mesh%nodes)
        
        do il = 1, element%n_edofs
            ig = element%dofs(il)
            if (ig > 0) then
                do jl = 1, element%n_edofs
                    jg = element%dofs(jl)
                    if (jg < 0) then
                        call Kab%add(ig, -jg, Ks(i)%at(il, jl))
                    else
                        call Kaa%add(ig, jg, Ks(i)%at(il, jl))
                    end if
                end do
            end if
        end do
    end do
    
    
    call Kaa%to_csr()
    call Kab%to_csr()
    
    deallocate(Ks)
    
    

    load(2*(5- 1) + 1) = 5.0
    load(2*(10- 1) + 1) = 5.0
    load(2*(15- 1) + 1) = 5.0
    load(2*(20 - 1) + 1) = 5.0
    load(2*(25 - 1) + 1) = 5.0
    
    
    
    pt(:) = 0
    maxfct = 1
    mnum = 1
    mtype = 11
    phase = 13
    n = Kaa%n_rows
    nrhs = 1
    msglvl = 0
    allocate(perm(n))
    
    do i = 1, 100000
    call pardiso (pt, maxfct, mnum, mtype, phase, n, Kaa%val, Kaa%row, Kaa%col, perm, nrhs, iparm, msglvl, load, x, error)
    end do
    
    deallocate(perm)
    
    
    
    lol = maxval(x)
    
    

    
!internal static SparseDOK GetGlobalStiffnessMatrix(ModelDatabase model)
!{
!	Matrix[] Kes = new Matrix[model.Mesh.Elements.Count];
!	Parallel.For(0, Kes.Length, i => Kes[i] = model.Mesh.Elements[i].GetStiffnessMatrix());
!
!	SparseDOK K = new(model.DegreesOfFreedom, model.DegreesOfFreedom);
!	for (int i = 0; i < Kes.Length; i++) LocalToGlobal_Matrix(K, Kes[i], model.Mesh.Elements[i]);
!	return K;
!}
    


    print *, 'Hi'

    end program

        !Ub = zeros(size(Kab, 2), 1);
        !for bc = model.boundaryConditions
        !    nodeSet = getField(model.mesh.nodeSets, bc.nodeSetName);
        !    nodeIndices = nodeSet.indices;
        !    for il = 1 : length(nodeIndices)
        !        ig = nodeIndices(il);
        !        for jjj = 1 : length(bc.activeDOFs)
        !            dim = bc.activeDOFs(jjj);
        !            ind = dofTable(dim, ig);
        !            Ub(-ind) = bc.values(jjj);
        !        end
        !    end
        !end
    !Pg = Pg - Kab*Ub;